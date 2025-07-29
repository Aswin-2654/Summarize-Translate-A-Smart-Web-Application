import os
import logging
from flask import Flask, render_template, request, jsonify, send_file, make_response
from utils.scraper import extract_article_content
from utils.summarizer import summarize_text, calculate_reading_time
from utils.translator import translate_text
from utils.pdf_generator import generate_pdf
from utils.pdf_extractor import extract_text_from_pdf
import urllib.parse
import tempfile

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure Flask for file uploads
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    """Process the URL or PDF, extract content, summarize, and translate"""
    try:
        target_language = request.form.get('language', 'en')
        article_content = None
        images = []
        source_type = None
        source_name = None
        
        # Check if it's a URL or PDF file upload
        url = request.form.get('url')
        pdf_file = request.files.get('pdf_file')
        
        if url and url.strip():
            # Process URL
            source_type = 'url'
            source_name = url
            
            # Validate URL
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return jsonify({'error': 'Invalid URL format'}), 400
            
            # Extract article content and images
            logger.debug(f"Extracting content from URL: {url}")
            article_content, images = extract_article_content(url)
            
            if not article_content or len(article_content.strip()) < 50:
                return jsonify({'error': 'Could not extract meaningful content from the provided URL'}), 400
            
        elif pdf_file and pdf_file.filename:
            # Process PDF file
            source_type = 'pdf'
            
            # Validate file extension
            if not allowed_file(pdf_file.filename):
                return jsonify({'error': 'Only PDF files are allowed'}), 400
            
            # Extract text from PDF
            logger.debug(f"Extracting content from PDF: {pdf_file.filename}")
            article_content, num_pages, source_name = extract_text_from_pdf(pdf_file)
            
        else:
            # Neither URL nor PDF file provided
            return jsonify({'error': 'Please provide a URL or upload a PDF file'}), 400
        
        # Generate summary
        logger.debug("Generating summary")
        summary = summarize_text(article_content)
        reading_time = calculate_reading_time(summary)
        
        # Translate summary if requested and not already in the target language
        if target_language != 'en':
            logger.debug(f"Translating summary to {target_language}")
            translated_summary = translate_text(summary, target_language)
            translated_reading_time = calculate_reading_time(translated_summary)
        else:
            translated_summary = summary
            translated_reading_time = reading_time
        
        # Prepare response
        result = {
            'source_type': source_type,
            'source_name': source_name,
            'original_url': url if source_type == 'url' else None,
            'article_content': article_content[:1000] + '...' if len(article_content) > 1000 else article_content,
            'summary': summary,
            'translated_summary': translated_summary,
            'target_language': target_language,
            'reading_time': reading_time,
            'translated_reading_time': translated_reading_time,
            'images': images if source_type == 'url' else []
        }
        
        return render_template('result.html', result=result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF with article summary"""
    try:
        summary = request.form.get('summary')
        translated_summary = request.form.get('translated_summary')
        source_type = request.form.get('source_type')
        source_name = request.form.get('source_name')
        target_language = request.form.get('target_language')
        reading_time = request.form.get('reading_time')
        
        if not summary or not source_name:
            return jsonify({'error': 'Missing required information'}), 400
        
        # Get original URL or source identifier
        original_source = source_name
        
        # Generate PDF
        pdf_file = generate_pdf(
            original_url=original_source,
            summary=summary,
            translated_summary=translated_summary,
            target_language=target_language,
            reading_time=reading_time,
            source_type=source_type
        )
        
        # Generate filename based on source
        filename = 'article_summary.pdf'
        if source_type == 'pdf':
            filename = f"summary_{os.path.basename(source_name)}"
        
        # Prepare response
        response = make_response(send_file(
            pdf_file,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        ))
        
        # Clean up temporary file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(pdf_file)
            except:
                pass
                
        return response
    
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'An error occurred while generating the PDF: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
