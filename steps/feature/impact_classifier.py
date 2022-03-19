from sklearn.base import BaseEstimator, TransformerMixin


class ImpactClassifier(BaseEstimator, TransformerMixin):

    def __init__(self, model):
        self.model = model

    def fit(self, X, y=None):
        self.model.fit(X, y)
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_['impact'] = self.model.predict(X_)
        return X_
