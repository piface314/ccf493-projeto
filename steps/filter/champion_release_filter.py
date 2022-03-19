from sklearn.base import BaseEstimator, TransformerMixin


class ChampionReleaseFilter(BaseEstimator, TransformerMixin):

    def __init__(self, champions_dict):
        self.cr_dict = champions_dict

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        releases = X['champion'].map(lambda c: self.cr_dict.get(c, None))
        return X[X['date'] > releases]
