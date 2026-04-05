@echo off
echo Installing required packages...
py -3.11 -m pip install streamlit==1.28.0 google-generativeai==0.3.2 PyPDF2==3.0.0 python-docx==1.1.0 python-dotenv==1.0.0
echo.
echo Installation complete!
echo.
echo Running the app...
py -3.11 -m streamlit run WORKING_app.py
pause