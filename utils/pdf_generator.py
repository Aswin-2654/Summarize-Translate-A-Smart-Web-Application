import tempfile
import os
import logging
from fpdf import FPDF
from datetime import datetime
from utils.translator import get_language_name

logger = logging.getLogger(__name__)

class ArticlePDF(FPDF):
    """Custom PDF class for article summary"""
    def header(self):
        # Set font
        self.set_font('Arial', 'B', 12)
        # Title
        self.cell(0, 10, 'Article Summary', 0, 1, 'C')
        # Line break
        self.ln(5)
    
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Set font
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        # Date
        self.cell(0, 10, datetime.now().strftime('%Y-%m-%d %H:%M'), 0, 0, 'R')

def generate_pdf(original_url, summary, translated_summary=None, target_language=None, reading_time=None, source_type=None):
    """
    Generate a PDF with the original and translated summaries
    
    Args:
        original_url (str): URL of the original article or PDF filename
        summary (str): Original summary text
        translated_summary (str): Translated summary text (optional)
        target_language (str): Target language code (optional)
        reading_time (str): Estimated reading time (optional)
        source_type (str): Type of source ('url' or 'pdf')
        
    Returns:
        str: Path to the generated PDF file
    """
    try:
        # Create a temporary file for the PDF
        fd, path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)  # Close file descriptor
        
        # Create PDF object
        pdf = ArticlePDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Set fonts
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        title = 'Article Summary'
        if source_type == 'pdf':
            title = 'PDF Document Summary'
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)
        
        # Source information
        pdf.set_font('Arial', '', 10)
        source_label = "Source URL:" if source_type == 'url' else "Source File:"
        pdf.multi_cell(0, 5, f"{source_label} {original_url}")
        pdf.ln(5)
        
        # Date and time
        pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        pdf.ln(10)
        
        # Original summary section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Summary (English)', 0, 1)
        
        if reading_time:
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 5, f"Estimated reading time: {reading_time}")
            pdf.ln(5)
        
        # Original summary content
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 5, summary)
        pdf.ln(10)
        
        # Translated summary section (if provided)
        if translated_summary and target_language and target_language != 'en':
            language_name = get_language_name(target_language)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f'Summary ({language_name})', 0, 1)
            
            # Translated reading time
            if reading_time:
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 5, f"Estimated reading time: {reading_time}")
                pdf.ln(5)
            
            # Translated summary content
            pdf.set_font('Arial', '', 11)
            pdf.multi_cell(0, 5, translated_summary)
        
        # Save the PDF to the temporary file
        pdf.output(path)
        
        logger.debug(f"PDF generated: {path}")
        return path
    
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise Exception(f"Failed to generate PDF: {str(e)}")
