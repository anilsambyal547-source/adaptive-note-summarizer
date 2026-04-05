import google.generativeai as genai

API_KEY = "AIzaSyBQ-jpxgGvQDP2lSygLrRqdsNwyYFbCReU"  # replace with your key

def test_key():
    try:
        genai.configure(api_key=API_KEY)
        print("✅ API Key configured")
        
        # List available models
        models = genai.list_models()
        print("\n📋 Available models:")
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Test a model
        test_model = genai.GenerativeModel('models/gemini-2.0-flash')
        response = test_model.generate_content("Say 'working'")
        print(f"\n✅ Test response: {response.text[:50]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_key()