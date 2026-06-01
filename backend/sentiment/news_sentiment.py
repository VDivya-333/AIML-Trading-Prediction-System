from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialize VADER analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(news_text):
    if not news_text:
        return {"sentiment_score": 0.0, "sentiment": "Neutral"}

    # VADER returns a dictionary with negative, neutral, positive, and compound scores
    vs = analyzer.polarity_scores(news_text)
    compound_score = vs['compound']
    


    sentiment_label = "Neutral"
    if compound_score >= 0.05:
        sentiment_label = "Positive"
    elif compound_score <= -0.05:
        sentiment_label = "Negative"
    
    return {"sentiment_score": compound_score, "sentiment": sentiment_label}

if __name__ == "__main__":
    print(analyze_sentiment("Bitcoin market is growing rapidly"))
    print(analyze_sentiment("The market is crashing today, very bad news."))
    print(analyze_sentiment("The stock market is open."))