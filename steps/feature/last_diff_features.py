from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd


class LastDiffFeatures(BaseEstimator, TransformerMixin):

    def __init__(self, dt_unit='W'):
        self.dt_unit = dt_unit

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        tuples = []
        c_champion, c_deltas = None, None
        delta_cols = ['popularity', 'winrate', 'banrate', 'date']
        for t in X.itertuples(index=False):
            if c_champion != t.champion:
                c_champion = t.champion
                c_deltas = [t.__getattribute__(c) for c in delta_cols]
            vals = [t.__getattribute__(c) - v for c, v in zip(delta_cols, c_deltas)]
            tuples.append((*t, *vals))
            if t.diff != 'none':
                c_deltas = [t.__getattribute__(c) for c in delta_cols]
        X_ = pd.DataFrame(tuples, columns=list(X.columns) + [c+'_delta' for c in delta_cols])
        X_['date_delta'] = X_['date_delta'].astype(f'timedelta64[{self.dt_unit}]')
        return X_
