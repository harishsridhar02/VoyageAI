# VoyageAI
#🌍 Travel Recommendation App
#An intelligent travel planner that delivers real-time, personalized travel suggestions using the Google Gemini API, Google Places API, and a Streamlit web interface. Designed for tourists and travel enthusiasts, this app simplifies destination discovery with AI-powered recommendations based on user preferences like location, interests, and budget.

✨ Features
🧠 Natural language understanding using Google Gemini API

📍 Real-time data fetching via Google Places API

🏨 Categorized suggestions: Hotels, Restaurants, Attractions

📊 Rating-based and location-biased filtering

🖥️ Interactive and lightweight Streamlit GUI

📌 Personalized travel experiences based on context

🚀 Tech Stack
Frontend: Streamlit (Python)

AI: Google Gemini (GenAI) for NLP and intent extraction

Backend: Python, Pandas, JSON handling

APIs: Google Places API

🧠 How It Works
User enters a natural language query (e.g., “Find the best restaurants in Paris under $50”)

Gemini API processes the intent and extracts details

Places API fetches real-time data based on extracted keywords

App filters results by rating, location, and type

Final suggestions are displayed with names, ratings, and images

📷 Demo
Insert GIF or screenshots here showing the input and personalized output

🔧 Setup & Installation
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Set Up API Keys

Obtain your Google Gemini API Key

Obtain your Google Places API Key

Create a .env file and add:

ini
Copy
Edit
GEMINI_API_KEY=your_key
GOOGLE_API_KEY=your_key
Run the App

bash
Copy
Edit
streamlit run app.py
🗺️ Architecture Overview
Input Layer: Streamlit captures user queries

Processing Layer: Gemini interprets intent; Python backend parses data

Data Layer: Google Places API fetches place details

Output Layer: Streamlit displays results in a user-friendly format

📚 Literature & Inspiration
Vaswani et al., Attention is All You Need, 2017

Raffel et al., Exploring Transfer Learning with T5, 2020

Lewis et al., BART: Denoising Pre-training, 2019

Google Gemini API Documentation

Google Places API Documentation

Streamlit Official Docs

✅ Future Enhancements
Add multi-city itinerary planner

Include travel cost estimations and filters

Integration with calendar/bookings

Voice-based input using Speech-to-Text
