from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np


class HistoryCombiner(BaseEstimator, TransformerMixin):

    def __init__(self, play_df, skins_df, play_metrics_agg='mean'):
        self.play_df = play_df
        self.skins_df = skins_df[skins_df['skin'] != 'Original']
        self.play_metrics_agg = play_metrics_agg

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        dates = np.sort(X['date'].unique())
        play_df = self.group_play(dates)
        skins_df = self.group_skins(dates)
        X_ = X.join(play_df, on=['date', 'champion'], how='outer')\
            .join(skins_df, on=['date', 'champion'], how='outer')\
            .fillna({'diff': 0, 'buff': 0, 'nerf': 0, 'skin': 0}, axis=0)\
            .drop('patch', axis=1)\
            .sort_values(by=['champion', 'date'])
        min_date, max_date = self.play_df['date'].min(), X['date'].max()
        X_ = X_[(min_date <= X_['date']) & (X_['date'] <= max_date)].reset_index(drop=True)
        return self.with_total_skins(self.fill_play(X_))\
            .dropna(axis=0).reset_index(drop=True)

    def group_skins(self, dates):
        return self.with_patch_date(dates, self.skins_df, 'release')\
            .groupby(['date', 'champion'])['skin']\
            .count()

    def group_play(self, dates):
        return self.with_patch_date(dates, self.play_df, 'date')\
            .groupby(['date', 'champion'])\
            .agg(self.play_metrics_agg)

    def with_patch_date(self, dates, df, key):
        bounds_df = df.copy()
        bounds_df['date'] = df[key]\
            .apply(self.upper_bound, args=(dates,))
        return bounds_df

    def upper_bound(self, x, dates):
        l, r = 0, len(dates)
        while (l < r):
            m = l + (r - l) // 2
            if x < dates[m]:
                r = m
            else:
                l = m + 1
        return dates[l] if 0 <= l < len(dates) else None

    def fill_play(self, X):
        n = len(X) - 1
        def fill(row, col):
            if not np.isnan(row[col]):
                return row[col]
            i, c = row['index'], row['champion']
            if i > 0 and X.iloc[i-1]['champion'] == c and i < n and X.iloc[i+1]['champion'] == c:
                return (X.iloc[i-1][col] + X.iloc[i+1][col]) / 2
        for col in ('popularity', 'winrate', 'banrate'):
            X[col] = X.reset_index().apply(fill, axis=1, args=(col,))
        return X

    def with_total_skins(self, X):
        X['total_skins'] = X.groupby('champion')['skin'].cumsum()
        return X
