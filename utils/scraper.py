import logging
import requests
from bs4 import BeautifulSoup
import trafilatura
from urllib.parse import urlparse, urljoin
import re

logger = logging.getLogger(__name__)

def extract_article_content(url):
    """
    Extract the main content from a given URL.
    Uses trafilatura first, then falls back to BeautifulSoup if needed.
    
    Args:
        url (str): URL of the article to extract
        
    Returns:
        tuple: (Extracted article text content, List of image URLs)
    """
    try:
        # Headers for requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Get the page content
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse with BeautifulSoup for image extraction
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract images
        images = []
        
        # First try with trafilatura for text content (better for article content)
        downloaded = trafilatura.fetch_url(url)
        text_content = ""
        if downloaded:
            text_content = trafilatura.extract(downloaded)
            if text_content and len(text_content.strip()) > 100:
                logger.debug("Content extracted using trafilatura")
        
        # If trafilatura didn't get good results, use BeautifulSoup
        if not text_content or len(text_content.strip()) <= 100:
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Try to find the main content
            main_content = None
            
            # Look for article tag
            article = soup.find('article')
            if article:
                main_content = article
            
            # If article tag not found, try common content div classes
            if not main_content:
                for div in soup.find_all('div', class_=['content', 'article', 'post', 'entry', 'main-content']):
                    if div.text and len(div.text.strip()) > 200:
                        main_content = div
                        break
            
            # If still not found, look for the div with the most paragraphs
            if not main_content:
                max_paragraphs = 0
                for div in soup.find_all('div'):
                    paragraphs = div.find_all('p')
                    if len(paragraphs) > max_paragraphs:
                        max_paragraphs = len(paragraphs)
                        main_content = div
            
            # Extract text from main content or fallback to all paragraphs
            if main_content:
                paragraphs = main_content.find_all('p')
                text_content = ' '.join([p.get_text().strip() for p in paragraphs])
            else:
                # Fallback: get all paragraphs in the document
                paragraphs = soup.find_all('p')
                text_content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Clean up the text content
            text_content = ' '.join(text_content.split())
            logger.debug("Content extracted using BeautifulSoup")
        
        # Try to extract images from the article content first
        # Ensure main_content is defined before attempting to use it
        if 'main_content' not in locals() or main_content is None:
            main_content = None
            
        content_area = soup.find('article') or main_content
        if content_area:
            # Find all images in the content area
            for img in content_area.find_all('img', src=True):
                src = img.get('src')
                if src and not src.startswith('data:'):
                    # Convert relative URLs to absolute
                    img_url = urljoin(url, src)
                    # Filter out small icons and advertisements
                    if not re.search(r'(icon|logo|avatar|banner|ad|pixel|tracking)', img_url.lower()):
                        images.append(img_url)
        
        # If no images found in content area, look for og:image meta tags
        if not images:
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                images.append(urljoin(url, og_image.get('content')))
        
        # If still no images, look for large images throughout the document
        if not images:
            for img in soup.find_all('img', src=True):
                src = img.get('src')
                if src and not src.startswith('data:'):
                    width = img.get('width')
                    height = img.get('height')
                    # Only include reasonably sized images
                    if (width and height and int(width) > 200 and int(height) > 200) or \
                       (not width and not height and not re.search(r'(icon|logo|avatar|banner|ad|pixel|tracking)', src.lower())):
                        img_url = urljoin(url, src)
                        images.append(img_url)
        
        # Limit to top 3 images
        images = images[:3]
        logger.debug(f"Extracted {len(images)} images from URL")
        
        return (text_content, images)
    
    except Exception as e:
        logger.error(f"Error extracting content from URL {url}: {str(e)}")
        raise Exception(f"Failed to extract content: {str(e)}")
