from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def analyze_sentiment(text: str) -> str:
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)['compound']
    
    if sentiment_score >= 0.05:
        return "Positive"
    elif sentiment_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"
