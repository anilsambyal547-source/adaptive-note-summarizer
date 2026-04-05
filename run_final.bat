@echo off
echo Installing required packages...
py -3.11 -m pip install streamlit==1.28.0 google-generativeai==0.3.2 PyPDF2==3.0.0 python-docx==1.1.0 --user

echo.
echo Testing API key...
py -3.11 -c "
import google.generativeai as genai
api_key = 'AIzaSyDGaLZGy6xAEFp8aIRNeKeDxOdqkbAApKc'
try:
    genai.configure(api_key=api_key)
    print('✅ API Key is valid')
    print('📊 Available models:')
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f'  - {model.name}')
except Exception as e:
    print(f'❌ Error: {e}')
"

echo.
echo Starting the app...
py -3.11 -m streamlit run WORKING_GEMINI_app.py
pause