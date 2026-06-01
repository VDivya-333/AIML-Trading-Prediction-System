from sklearn.linear_model import LogisticRegression
import logging

logger = logging.getLogger(__name__)

def train_signal_model(X, y):
    """
    Trains a Logistic Regression model to classify trading signals.
    Currently used as a secondary signal verification method.
    """
    try:
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        logger.info("Logistic Regression Classifier trained successfully.")
    except Exception as e:
        logger.error(f"Error training signal classifier: {e}")