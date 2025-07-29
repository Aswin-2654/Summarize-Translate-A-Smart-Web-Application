import logging
import os
import PyPDF2
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file
    
    Args:
        pdf_file: The uploaded PDF file object
        
    Returns:
        tuple: (Extracted text content, number of pages, filename)
    """
    try:
        # Get the original filename
        original_filename = secure_filename(pdf_file.filename)
        
        # Create PDF reader object
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Get number of pages
        num_pages = len(reader.pages)
        
        # Check page limit (50 pages)
        if num_pages > 50:
            raise ValueError("PDF exceeds the 50-page limit")
        
        # Extract text from all pages
        text_content = ""
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text_content += page.extract_text()
        
        if not text_content or len(text_content.strip()) < 50:
            raise ValueError("Could not extract meaningful content from the PDF")
        
        logger.debug(f"Extracted {num_pages} pages from PDF: {original_filename}")
        return text_content, num_pages, original_filename
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract PDF content: {str(e)}")