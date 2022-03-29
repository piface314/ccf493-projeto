import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


class ChangedClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, model, threshold=0.5):
        self.model = model
        self.threshold = threshold

    def fit(self, X, y):
        X, y = check_X_y(X, y)
        self.model.fit(X, y)
        return self

    def predict(self, X):
        check_is_fitted(self.model)
        X = check_array(X)
        prob = self.model.predict_proba(X)
        return np.array([ps[1] >= self.threshold for ps in prob])
