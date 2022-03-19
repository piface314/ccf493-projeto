from sklearn.base import BaseEstimator, TransformerMixin


class ImpactAggregator(BaseEstimator, TransformerMixin):

    def __init__(self, sort=False):
        self.sort = sort

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        X_['buff'] = X_['diff'].map(lambda x: max(x, 0))
        X_['nerf'] = X_['diff'].map(lambda x: abs(min(x, 0)))
        X_ = X_.groupby(['patch', 'date', 'champion']).sum().reset_index()
        if self.sort:
            X_ = X_.sort_values(['date', 'champion'], ascending=[False, True])\
                    .reset_index().drop('index', axis=1)
        return X_
