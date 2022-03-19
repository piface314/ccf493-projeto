from sklearn.base import BaseEstimator, TransformerMixin


class ImpactFilter(BaseEstimator, TransformerMixin):

    def __init__(self, ignore=set()):
        self.ignore = ignore

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[~X['impact'].isin(self.ignore)]
