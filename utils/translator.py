import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

# Language codes and their display names
LANGUAGE_CODES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh-CN': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ar': 'Arabic'
}

def get_language_name(code):
    """
    Get the display name for a language code
    
    Args:
        code (str): Language code (e.g., 'en', 'es')
        
    Returns:
        str: Language name
    """
    return LANGUAGE_CODES.get(code, code)

def translate_text(text, target_language='en'):
    """
    Translate text to the target language using the Google Translator API
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code (default: 'en')
        
    Returns:
        str: Translated text
    """
    try:
        # Skip translation if already in the target language or if text is too long
        if target_language == 'en' or not text:
            return text
        
        # Google Translator has character limits, so we need to split the text
        MAX_CHARS = 5000
        
        if len(text) <= MAX_CHARS:
            # Translate the entire text if it's within limits
            translator = GoogleTranslator(source='auto', target=target_language)
            translated_text = translator.translate(text)
            return translated_text
        else:
            # Split the text into sentences and translate them in batches
            translator = GoogleTranslator(source='auto', target=target_language)
            
            # Split by sentences to maintain context
            sentences = text.split('. ')
            
            translated_parts = []
            current_batch = ""
            
            for sentence in sentences:
                # If adding this sentence would exceed the limit, translate the current batch
                if len(current_batch) + len(sentence) + 2 > MAX_CHARS:
                    if current_batch:
                        translated_parts.append(translator.translate(current_batch))
                    current_batch = sentence + ". "
                else:
                    current_batch += sentence + ". "
            
            # Translate any remaining text
            if current_batch:
                translated_parts.append(translator.translate(current_batch))
            
            # Join the translated parts
            return ' '.join(translated_parts)
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        # Return original text if translation fails
        return f"Translation error: {str(e)}\n\nOriginal text: {text}"
