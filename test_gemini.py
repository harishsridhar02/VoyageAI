import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini():
    print("Testing Gemini API setup...")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
        
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        models = [m.name for m in genai.list_models()]
        print("Available models:", models)
        
        # Filter for stable Gemini models, excluding vision and deprecated versions
        preferred_models = [
            m for m in models 
            if 'gemini' in m.lower() 
            and 'pro' in m.lower()
            and 'vision' not in m.lower()
            and '1.0' not in m
            and 'exp' not in m.lower()
        ]
        
        if not preferred_models:
            print("❌ No suitable Gemini models found")
            return False
            
        # Use gemini-1.5-pro if available, otherwise use first available model
        model_name = next(
            (m for m in preferred_models if 'gemini-1.5-pro' in m),
            preferred_models[0]
        )
        print(f"Using model: {model_name}")
        model = genai.GenerativeModel(model_name)

        # Test generation
        response = model.generate_content("Hello, testing connection!")
        print("✓ API Response:", response.text)
        print("\n✓ Gemini API is working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("→ Verify API access at: https://makersuite.google.com/app/apikey")
        return False

if __name__ == "__main__":
    test_gemini()
