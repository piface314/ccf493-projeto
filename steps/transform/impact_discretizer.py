from sklearn.base import BaseEstimator, TransformerMixin


class ImpactDiscretizer(BaseEstimator, TransformerMixin):

    def __init__(self, eps=1e-4):
        self.eps = eps

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_['diff'] = X_.apply(self.__discretize, axis=1)
        return X_

    def __discretize(self, row):
        buff, nerf = row['buff'], row['nerf']
        if buff < self.eps and nerf < self.eps:
            return 'none'
        elif buff < self.eps:
            return 'nerf'
        elif nerf < self.eps:
            return 'buff'
        else:
            return 'adjust'
