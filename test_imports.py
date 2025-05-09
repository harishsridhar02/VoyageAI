import warnings
import logging
# Suppress Streamlit warning
logging.getLogger('streamlit').setLevel(logging.ERROR)

print("Testing imports...")

try:
    # Test base imports
    import pandas as pd
    import requests
    from dotenv import load_dotenv
    import folium
    print("✓ Base packages imported successfully")
    
    # Test Streamlit related imports
    import streamlit as st
    from streamlit_folium import folium_static
    print("✓ Streamlit packages imported successfully")
    
    # Test AI/ML imports
    from langchain_community.chat_models import ChatOpenAI
    import tiktoken
    print("✓ AI/ML packages imported successfully")
    
    # Test environment loading
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())
    print("✓ Environment loading successful!")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("Please reinstall the package that caused the error")
