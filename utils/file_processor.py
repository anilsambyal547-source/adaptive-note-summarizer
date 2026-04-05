# utils/file_processor.py - COMPLETE FILE PROCESSOR
import PyPDF2
import docx
import io

class FileProcessor:
    """Handles all file processing for PDF, TXT, DOCX"""
    
    @staticmethod
    def extract_text_from_file(uploaded_file):
        """Extract text from uploaded file"""
        try:
            file_name = uploaded_file.name.lower()
            
            if file_name.endswith('.pdf'):
                return FileProcessor._process_pdf(uploaded_file)
            elif file_name.endswith('.txt'):
                return FileProcessor._process_txt(uploaded_file)
            elif file_name.endswith('.docx'):
                return FileProcessor._process_docx(uploaded_file)
            else:
                return "Unsupported file format"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def _process_pdf(uploaded_file):
        """Process PDF files"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n\n"
        
        return text
    
    @staticmethod
    def _process_txt(uploaded_file):
        """Process TXT files"""
        return uploaded_file.read().decode('utf-8')
    
    @staticmethod
    def _process_docx(uploaded_file):
        """Process DOCX files"""
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        text = ""
        
        for para in doc.paragraphs:
            text += para.text + "\n"
        
        return text
    
    @staticmethod
    def get_file_stats(text):
        """Get statistics about the text"""
        words = len(text.split())
        chars = len(text)
        lines = text.count('\n') + 1
        
        return {
            "words": words,
            "characters": chars,
            "lines": lines
        }
