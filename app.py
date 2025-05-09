# Import libraries
import streamlit as st
import pandas as pd
import json
import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel
import folium
from streamlit_folium import folium_static
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential
from cachetools import TTLCache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize cache
cache = TTLCache(maxsize=100, ttl=3600)

# Load environment variables
load_dotenv()

# API Keys handling
api_key = os.getenv('PLACES_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    st.error("Google Places API key is missing. Please check your .env file.")
    st.stop()

if not gemini_api_key:
    st.error("Gemini API key is missing. Please check your .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=gemini_api_key)

# Constants
PLACES_API_URL = 'https://places.googleapis.com/v1/places:searchText'
DEFAULT_TIMEOUT = 30

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_api_request(url: str, headers: Dict, data: Dict, timeout: int = DEFAULT_TIMEOUT) -> Dict:
    """Make API request with retry logic"""
    try:
        response = requests.post(url, json=data, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API request failed: {str(e)}")
        raise

@st.cache_resource(ttl=300)
def init_connection():
    """Initialize connection and cache directories"""
    try:
        cache_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
        os.makedirs(cache_dir, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False

def get_place_data(query: str, api_key: str, location_bias: Dict = None, min_rating: float = None) -> pd.DataFrame:
    """
    Place Search Algorithm:
    1. Query construction with location bias
    2. API request with retry logic
    3. Response parsing and normalization
    4. DataFrame conversion
    
    Time Complexity: O(r) where r is API response size
    Space Complexity: O(p) where p is number of places returned
    """
    headers = {
        'Content-Type': 'application/json',
        'X-Goog-Api-Key': os.getenv("PLACES_API_KEY", "your_default_api_key_here"),
        'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.websiteUri,places.location,places.googleMapsUri'
    }
    
    data = {
        'textQuery': query,
        'minRating': min_rating,
        'locationBias': location_bias
    }
    
    result = make_api_request(PLACES_API_URL, headers, data)
    if 'places' not in result:
        return pd.DataFrame()
        
    df = pd.json_normalize(result['places'])
    return df

def setup_chatbot(api_key: str):
    """Initialize Gemini chatbot"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        logger.error(f"Chatbot setup failed: {e}")
        return None

def get_help_text():
    return """🤖 Available Commands:
    1. 'top 5 hotels' - Show 5 highest rated hotels
    2. 'best food' or 'restaurants' - Show top rated restaurants
    3. 'attractions nearby' - List tourist spots with ratings
    4. 'rating [place name]' - Get rating for specific place
    5. 'info [place name]' - Get full details about a place
    6. 'cheap hotels' - Show budget-friendly accommodations
    7. 'popular places' - Most visited places based on ratings
    8. 'distance [place name]' - Get distance from city center
    9. 'website [place name]' - Get direct website link
    10. 'compare [hotels/restaurants]' - Compare places by rating and reviews
    
💡 Try questions like:
- "What's the highest rated restaurant?"
- "Show me family-friendly hotels"
- "Which attractions have the most reviews?"
"""

def handle_command(prompt: str, df_place_rename: pd.DataFrame):
    """
    Command Processing Algorithm:
    1. Command normalization (lowercase, strip)
    2. Pattern matching (startswith, contains)
    3. DataFrame filtering and sorting
    4. Result formatting
    
    Time Complexity: O(n) where n is number of places
    Space Complexity: O(k) where k is filtered results
    """
    cmd = prompt.lower().strip()
    
    if cmd.startswith('top 5'):
        place_type = cmd.replace('top 5', '').strip()
        filtered_df = df_place_rename[df_place_rename['Type'].str.lower() == place_type]
        return filtered_df.head(5).to_string()
        
    elif cmd.startswith('rating '):
        place_name = cmd.replace('rating', '').strip()
        place = df_place_rename[df_place_rename['Name'].str.lower().str.contains(place_name.lower())]
        if not place.empty:
            return f"Rating for {place.iloc[0]['Name']}: {place.iloc[0]['Rating']} ({place.iloc[0]['User Rating Count']} reviews)"
            
    elif cmd == 'popular places':
        return df_place_rename.sort_values('User Rating Count', ascending=False).head(3).to_string()
        
    return None  # Return None if no specific command matched

def main():
    # Add connection check with retry option
    if not init_connection():
        st.error("Server connection failed.")
        if st.button("Retry Connection"):
            st.experimental_rerun()
        return

    st.sidebar.title("VoyageAI 🌎")


    st.sidebar.write('Please fill in the fields below.')
    destination = st.sidebar.text_input('Destination:',key='destination_app')
    min_rating = st.sidebar.number_input('Minimum Rating:',value=4.0,min_value=0.5,max_value=4.5,step=0.5,key='minrating_app')
    radius = st.sidebar.number_input('Search Radius in meter:',value=3000,min_value=500,max_value=50000,step=100,key='radius_app')
    
    api_key = os.getenv("PLACES_API_KEY")
    if not api_key:
        st.error("API key for Google Places is missing. Please set the 'PLACES_API_KEY' environment variable.")
        return

    if destination:
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.location',
            }
        data = {
            'textQuery': destination,
            'maxResultCount': 1,
        }

        # Convert data to JSON format
        json_data = json.dumps(data)

        # Make the POST request
        response = requests.post(PLACES_API_URL, data=json_data, headers=headers)

        # Print the response
        result = response.json()

        # Convert JSON data to DataFrame
        df = pd.json_normalize(result['places'])
        
        # Get the latitude and longitude values
        initial_latitude = df['location.latitude'].iloc[0]
        initial_longitude = df['location.longitude'].iloc[0]

        # Create the circle
        circle_center = {"latitude": initial_latitude, "longitude": initial_longitude}
        circle_radius = radius
        
        headers_place = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel,places.userRatingCount,places.rating,places.websiteUri,places.location,places.googleMapsUri',
        }

        def hotel(): 
            data_hotel = {
                'textQuery': f'Place to stay near {destination}',
                'minRating': min_rating,
                'locationBias': {
                    "circle": {
                        "center": circle_center,
                        "radius": circle_radius
                    }
                }
            }

            # Convert data to JSON format
            json_data_hotel = json.dumps(data_hotel)  
            # Make the POST request
            response_hotel = requests.post(PLACES_API_URL, data=json_data_hotel, headers=headers_place)
            # Print the response
            result_hotel = response_hotel.json()
            # Convert JSON data to DataFrame
            df_hotel = pd.json_normalize(result_hotel['places'])
            # Add 'type'
            df_hotel['type'] = 'Hotel'
            return df_hotel
    
        def restaurant():  
            data_restaurant = {
                'textQuery': f'Place to eat near {destination}',
                'minRating': min_rating,
                'locationBias': {
                    "circle": {
                        "center": circle_center,
                        "radius": circle_radius
                    }
                }
            }

            # Convert data to JSON format
            json_data_restaurant = json.dumps(data_restaurant)  
            # Make the POST request
            response_restaurant = requests.post(PLACES_API_URL, data=json_data_restaurant, headers=headers_place)
            # Print the response
            result_restaurant = response_restaurant.json()
            # Convert JSON data to DataFrame
            df_restaurant = pd.json_normalize(result_restaurant['places'])
            # Add 'type'
            df_restaurant['type'] = 'Restaurant'
            return df_restaurant
    
        def tourist():  
            data_tourist = {
                'textQuery': f'Tourist attraction near {destination}',
                'minRating': min_rating,
                'locationBias': {
                    "circle": {
                        "center": circle_center,
                        "radius": circle_radius
                    }
                }
            }

            # Convert data to JSON format
            json_data_tourist = json.dumps(data_tourist)  
            # Make the POST request
            response_tourist = requests.post(PLACES_API_URL, data=json_data_tourist, headers=headers_place)
            # Print the response
            result_tourist = response_tourist.json()
            # Convert JSON data to DataFrame
            df_tourist = pd.json_normalize(result_tourist['places'])
            # Add 'type'
            df_tourist['type'] = 'Tourist'
            return df_tourist
    
        df_hotel = hotel()
        df_restaurant = restaurant()
        df_tourist = tourist()

    # Assuming all three dataframes have similar columns
        df_place = pd.concat([df_hotel, df_restaurant, df_tourist], ignore_index=True)
        df_place = df_place.sort_values(by=['userRatingCount', 'rating'], ascending=[False, False]).reset_index(drop=True)
        
        df_place_rename = df_place[['type','displayName.text','formattedAddress','rating', 'userRatingCount','googleMapsUri', 'websiteUri', 'location.latitude', 'location.longitude', 'displayName.languageCode']]
        df_place_rename = df_place_rename.rename(columns={
            'displayName.text': 'Name',
            'rating': 'Rating',
            'googleMapsUri': 'Google Maps URL',
            'websiteUri': 'Website URL',
            'userRatingCount': 'User Rating Count',
            'location.latitude': 'Latitude',
            'location.longitude': 'Longitude',
            'formattedAddress': 'Address',
            'displayName.languageCode': 'Language Code',
            'type': 'Type'
        })
        def database():
            st.dataframe(df_place_rename)

        def maps():
            st.header("🌏 VoyageAI 🌏")

            places_type = st.radio('Looking for: ',["Hotels 🏨", "Restaurants 🍴","Tourist Attractions ⭐"])
            initial_location = [initial_latitude, initial_longitude]
            type_colour = {'Hotel':'blue', 'Restaurant':'green', 'Tourist':'orange'}
            type_icon = {'Hotel':'home', 'Restaurant':'cutlery', 'Tourist':'star'}

            st.write(f"# Here are our recommendations for {places_type} near {destination} ")

            if places_type == 'Hotels 🏨': 
                df_place = df_hotel
                with st.spinner("Just a moment..."):
                    for index,row in df_place.iterrows():
                        location = [row['location.latitude'], row['location.longitude']]
                        mymap  = folium.Map(location = initial_location, 
                                zoom_start=9, control_scale=True)
                        content = (str(row['displayName.text']) + '<br>' + 
                                'Rating: '+ str(row['rating']) + '<br>' + 
                                'Address: ' + str(row['formattedAddress']) + '<br>' + 
                                'Website: '  + str(row['websiteUri'])
                                )
                        iframe = folium.IFrame(content, width=300, height=125)
                        popup = folium.Popup(iframe, max_width=300)

                        icon_color = type_colour[row['type']]
                        icon_type = type_icon[row['type']]
                        icon = folium.Icon(color=icon_color, icon=icon_type)

                        # Use different icons for hotels, restaurants, and tourist attractions
                        folium.Marker(location=location, popup=popup, icon=icon).add_to(mymap)

                        st.write(f"## {index + 1}. {row['displayName.text']}")
                        folium_static(mymap)
                        st.write(f"Rating: {row['rating']}")
                        st.write(f"Address: {row['formattedAddress']}")
                        st.write(f"Website: {row['websiteUri']}")
                        st.write(f"More information: {row['googleMapsUri']}\n")
                            
            elif places_type == 'Restaurants 🍴': 
                df_place = df_restaurant
                with st.spinner("Just a moment..."):
                    for index,row in df_place.iterrows():
                        location = [row['location.latitude'], row['location.longitude']]
                        mymap  = folium.Map(location = initial_location, 
                                zoom_start=9, control_scale=True)
                        content = (str(row['displayName.text']) + '<br>' + 
                                'Rating: '+ str(row['rating']) + '<br>' + 
                                'Address: ' + str(row['formattedAddress']) + '<br>' + 
                                'Website: '  + str(row['websiteUri'])
                                )
                        iframe = folium.IFrame(content, width=300, height=125)
                        popup = folium.Popup(iframe, max_width=300)

                        icon_color = type_colour[row['type']]
                        icon_type = type_icon[row['type']]
                        icon = folium.Icon(color=icon_color, icon=icon_type)

                        # Use different icons for hotels, restaurants, and tourist attractions
                        folium.Marker(location=location, popup=popup, icon=icon).add_to(mymap)

                        st.write(f"## {index + 1}. {row['displayName.text']}")
                        folium_static(mymap)
                        st.write(f"Rating: {row['rating']}")
                        st.write(f"Address: {row['formattedAddress']}")
                        st.write(f"Website: {row['websiteUri']}")
                        st.write(f"More information: {row['googleMapsUri']}\n")
            else:
                df_place = df_tourist
                with st.spinner("Just a moment..."):
                    for index,row in df_place.iterrows():
                        location = [row['location.latitude'], row['location.longitude']]
                        mymap  = folium.Map(location = initial_location, 
                                zoom_start=9, control_scale=True)
                        content = (str(row['displayName.text']) + '<br>' + 
                                'Rating: '+ str(row['rating']) + '<br>' + 
                                'Address: ' + str(row['formattedAddress']) + '<br>' + 
                                'Website: '  + str(row['websiteUri'])
                                )
                        iframe = folium.IFrame(content, width=300, height=125)
                        popup = folium.Popup(iframe, max_width=300)

                        icon_color = type_colour[row['type']]
                        icon_type = type_icon[row['type']]
                        icon = folium.Icon(color=icon_color, icon=icon_type)

                        # Use different icons for hotels, restaurants, and tourist attractions
                        folium.Marker(location=location, popup=popup, icon=icon).add_to(mymap)

                        st.write(f"## {index + 1}. {row['displayName.text']}")
                        folium_static(mymap)
                        st.write(f"Rating: {row['rating']}")
                        st.write(f"Address: {row['formattedAddress']}")
                        st.write(f"Website: {row['websiteUri']}")
                        st.write(f"More information: {row['googleMapsUri']}\n")


        def chatbot():
            try:
                # Initialize Gemini
                model = genai.GenerativeModel('gemini-1.5-pro')
                
                # Initialize chat history
                if "messages" not in st.session_state:
                    st.session_state.messages = [{"role": "assistant", 
                        "content": "Hi! I can help you find places. Type 'help' to see what I can do!"}]

                # Display chat history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])

                if prompt := st.chat_input("Type a command or ask a question (type 'help' for options)"):
                    st.chat_message("user").write(prompt)
                    
                    try:
                        # Handle commands first
                        if prompt.lower().strip() == 'help':
                            help_text = get_help_text()
                            with st.chat_message("assistant"):
                                st.write(help_text)
                            st.session_state.messages.append({"role": "user", "content": prompt})
                            st.session_state.messages.append({"role": "assistant", "content": help_text})
                            return
                        
                        # Try to handle as command
                        command_response = handle_command(prompt, df_place_rename)
                        if command_response:
                            with st.chat_message("assistant"):
                                st.write(command_response)
                            st.session_state.messages.append({"role": "user", "content": prompt})
                            st.session_state.messages.append({"role": "assistant", "content": command_response})
                            return
                        
                        # If not a command, process as natural language query
                        # Get places summary
                        places_summary = []
                        for type_df, type_name in [(df_hotel, "Hotels"), (df_restaurant, "Restaurants"), (df_tourist, "Tourist Spots")]:
                            if not type_df.empty:
                                top = type_df.head(1)
                                for _, row in top.iterrows():
                                    places_summary.append(f"{type_name}: {row['displayName.text']} (Rating: {row['rating']})")

                        # Create prompt
                        system_msg = f"""You are a helpful travel assistant for {destination}.
                        Here are the top rated places:
                        {chr(10).join(places_summary)}
                        
                        Provide a very brief response (max 2 sentences) about the places that match the user's question."""

                        # Generate response
                        response = model.generate_content(f"{system_msg}\nUser: {prompt}")
                        response_text = response.text

                        # Display response
                        with st.chat_message("assistant"):
                            st.write(response_text)

                        # Update chat history
                        st.session_state.messages.append({"role": "user", "content": prompt})
                        st.session_state.messages.append({"role": "assistant", "content": response_text})

                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")

            except Exception as e:
                st.error(f"Error in chatbot: {str(e)}")

        method = st.sidebar.radio(" ",["Search 🔎","ChatBot 🤖","Database 📑"], key="method_app")
        if method == "Search 🔎":
            maps()
        elif method == "ChatBot 🤖":
            chatbot()
        else:
            database()

    
        
if __name__ == '__main__':
    main()






