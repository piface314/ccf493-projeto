from sklearn.base import BaseEstimator, TransformerMixin


class PatchNoteTransformer(BaseEstimator, TransformerMixin):

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X['about'].fillna("") + ": " + X['text'].fillna("")
