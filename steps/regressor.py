import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted


class ConstantRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, c=None):
        self.c = c

    def fit(self, X, y):
        X, y = check_X_y(X, y)

        if self.c is None:
            self.const_ = y.mean()
        else:
            self.const_ = self.c
        return self

    def predict(self, X):
        check_is_fitted(self)
        X = check_array(X)

        return np.array(X.shape[0]*[self.const_])
