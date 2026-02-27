"""
Sentiment analysis module using NLTK VADER
"""
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import logging

# Download VADER lexicon if not already present
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Sentiment analyzer using VADER (Valence Aware Dictionary and sEntiment Reasoner)"""
    
    def __init__(self):
        """Initialize the VADER sentiment analyzer"""
        self.analyzer = SentimentIntensityAnalyzer()
        self.model_version = "VADER-v1.0"
        logger.info("✅ Sentiment analyzer initialized (VADER)")
    
    def analyze_text(self, text):
        """
        Analyze sentiment of a single text
        
        Args:
            text (str): The text to analyze
            
        Returns:
            dict: Sentiment scores including compound, pos, neg, neu
        """
        if not text or not isinstance(text, str):
            return {
                'compound': 0.0,
                'pos': 0.0,
                'neg': 0.0,
                'neu': 1.0,
                'confidence': 0.5
            }
        
        # Get sentiment scores
        scores = self.analyzer.polarity_scores(text)
        
        # Add confidence based on text length (longer text = more confident)
        word_count = len(text.split())
        confidence = min(0.5 + (word_count / 100) * 0.5, 0.95)
        
        return {
            'compound': scores['compound'],
            'pos': scores['pos'],
            'neg': scores['neg'],
            'neu': scores['neu'],
            'confidence': confidence
        }
    
    def analyze_news_article(self, title, description=None):
        """
        Analyze sentiment of a news article
        
        Args:
            title (str): Article title
            description (str): Article description/summary
            
        Returns:
            dict: Sentiment analysis results
        """
        # Combine title and description for better analysis
        text = title
        if description:
            text = text + " " + description
        
        scores = self.analyze_text(text)
        
        # Classify sentiment
        if scores['compound'] >= 0.05:
            sentiment_label = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'score': scores['compound'],
            'label': sentiment_label,
            'confidence': scores['confidence'],
            'positive_prob': scores['pos'],
            'negative_prob': scores['neg'],
            'neutral_prob': scores['neu'],
            'model_version': self.model_version
        }
    
    def analyze_batch(self, articles):
        """
        Analyze sentiment for multiple articles
        
        Args:
            articles (list): List of article dictionaries with 'title' and optional 'description'
            
        Returns:
            list: Sentiment results for each article
        """
        results = []
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            
            result = self.analyze_news_article(title, description)
            results.append(result)
        
        return results


# Quick test
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test with sample headlines
    test_headlines = [
        "Apple announces record profits, stock soars",
        "Tesla recalls thousands of vehicles due to safety concerns",
        "Microsoft acquires AI startup for $1 billion",
        "Fed announces interest rate decision"
    ]
    
    print("\n🔍 Testing Sentiment Analyzer")
    print("="*50)
    for headline in test_headlines:
        result = analyzer.analyze_news_article(headline)
        print(f"\n📰 {headline}")
        print(f"   Sentiment: {result['label'].upper()}")
        print(f"   Score: {result['score']:.2f}")
        print(f"   Confidence: {result['confidence']:.2%}")