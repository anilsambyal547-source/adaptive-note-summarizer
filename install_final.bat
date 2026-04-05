@echo off
echo Installing required packages...
py -3.11 -m pip install streamlit==1.28.0 google-generativeai==0.3.2 PyPDF2==3.0.0 python-docx==1.1.0 --user

echo.
echo Running test...
py -3.11 -c "import google.generativeai as genai; genai.configure(api_key='AIzaSyD5lQ0L8a6smw0kCcV8sZibL0H_CDZDB7M'); print('✅ API Key valid')"

echo.
echo Starting app...
py -3.11 -m streamlit run FINAL_app.py
pause