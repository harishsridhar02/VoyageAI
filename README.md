# 🌍 VoyageAI – Travel Recommendation App

**VoyageAI** is an intelligent travel planner that delivers real-time, personalized travel suggestions using the **Google Gemini API**, **Google Places API**, and a sleek **Streamlit** interface.  
Tailored for tourists, solo travellers, and adventure seekers, the app simplifies destination discovery with AI-powered recommendations based on location, interests, and budget.

---

## ✨ Features

- 🧠 Natural language understanding using **Google Gemini API**
- 📍 Real-time data fetching via **Google Places API**
- 🏨 Categorized suggestions: **Hotels, Restaurants, Attractions**
- 📊 Filtering based on ratings and proximity
- 🖥️ Interactive and lightweight **Streamlit GUI**
- 📌 Context-aware travel recommendations

---

## 🚀 Tech Stack

- **Frontend**: Streamlit (Python)
- **AI/NLP**: Google Gemini API (GenAI)
- **Backend**: Python, Pandas, JSON handling
- **APIs**: Google Places API

---

## 🧠 How It Works

1. **User Input**: Enter a natural language query (e.g., “Best tourist spots in Rome under $100”)
2. **Intent Extraction**: Gemini API processes and extracts keywords (location, interest, budget)
3. **Data Fetching**: Google Places API fetches live details like names, reviews, ratings
4. **Filtering**: Results are refined based on rating, type, and relevance
5. **Display**: Final suggestions shown in an organized, interactive format

---
## Architecture Overview
[User Input: Streamlit]
        ↓
[Intent Processing: Google Gemini API]
        ↓
[Keyword Extraction & Filtering: Python Backend]
        ↓
[Real-Time Place Data: Google Places API]
        ↓
[Recommendation Output: Streamlit Display]


## Futre Improvements:
🧳 Multi-city itinerary planner

💸 Travel cost estimations and filters

📅 Integration with calendars and booking platforms

🎙️ Voice-based input with Speech-to-Text support
