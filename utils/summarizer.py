import spacy
import numpy as np
import re
from collections import Counter
import logging

# Load spaCy language model
try:
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("sentencizer")
except OSError:
    # If model not installed, use a basic English model
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

logger = logging.getLogger(__name__)

def preprocess_text(text):
    """
    Preprocess text by removing special characters, numbers, and extra whitespace
    
    Args:
        text (str): Input text
        
    Returns:
        str: Preprocessed text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove numbers and special characters
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def calculate_word_frequencies(text):
    """
    Calculate word frequencies from the text after removing stopwords
    
    Args:
        text (str): Input text
        
    Returns:
        dict: Word frequencies dictionary
    """
    # Process text with spaCy
    doc = nlp(text)
    
    # Filter out stopwords and punctuation
    words = [token.text for token in doc if not token.is_stop and not token.is_punct]
    
    # Calculate word frequencies
    word_freq = Counter(words)
    
    # Normalize frequencies
    max_freq = max(word_freq.values()) if word_freq else 1
    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq
    
    return word_freq

def score_sentences(sentences, word_freq):
    """
    Score sentences based on word frequencies
    
    Args:
        sentences (list): List of sentences
        word_freq (dict): Word frequencies
        
    Returns:
        dict: Sentence scores
    """
    sentence_scores = {}
    
    for i, sentence in enumerate(sentences):
        # Process sentence with spaCy
        doc = nlp(sentence)
        
        # Filter out stopwords and count words
        word_count = len([token for token in doc if not token.is_stop and not token.is_punct])
        
        # Skip very short sentences
        if word_count < 3:
            continue
        
        # Calculate score based on word frequencies
        score = 0
        for token in doc:
            if token.text.lower() in word_freq:
                score += word_freq[token.text.lower()]
        
        # Normalize by sentence length to prevent bias toward longer sentences
        sentence_scores[i] = score / max(1, word_count)
    
    return sentence_scores

def summarize_text(text, summary_percentage=0.3, min_sentences=3, max_sentences=10):
    """
    Summarize the given text using extractive summarization
    
    Args:
        text (str): The text to summarize
        summary_percentage (float): Percentage of original sentences to include (default: 0.3)
        min_sentences (int): Minimum number of sentences in summary
        max_sentences (int): Maximum number of sentences in summary
        
    Returns:
        str: Summarized text
    """
    try:
        # Break the text into sentences
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # If text is very short, return as is
        if len(sentences) <= min_sentences:
            return text
        
        # Preprocess text
        preprocessed_text = preprocess_text(text)
        
        # Calculate word frequencies
        word_freq = calculate_word_frequencies(preprocessed_text)
        
        # Score sentences
        sentence_scores = score_sentences(sentences, word_freq)
        
        # Determine number of sentences for the summary
        num_sentences = max(min_sentences, min(max_sentences, int(len(sentences) * summary_percentage)))
        
        # Get the top-scored sentences
        top_sentence_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        
        # Sort the selected sentences by their original order
        top_sentence_indices = sorted(top_sentence_indices)
        
        # Build the summary
        summary = ' '.join([sentences[i] for i in top_sentence_indices])
        
        return summary
    
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        # Fallback to a simple summary if the sophisticated method fails
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        num_sentences = max(min_sentences, min(max_sentences, int(len(sentences) * summary_percentage)))
        return ' '.join(sentences[:num_sentences])

def calculate_reading_time(text, words_per_minute=200):
    """
    Calculate the estimated reading time for a text
    
    Args:
        text (str): The text to calculate reading time for
        words_per_minute (int): Average reading speed in words per minute
        
    Returns:
        str: Formatted reading time (e.g., "2 min read")
    """
    # Count words in the text
    word_count = len(text.split())
    
    # Calculate reading time in minutes
    minutes = max(1, round(word_count / words_per_minute))
    
    return f"{minutes} min read"
