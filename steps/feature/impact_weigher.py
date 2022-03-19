from functools import reduce
from itertools import chain
from math import floor, log10
from sklearn.base import BaseEstimator, TransformerMixin
import re

class ImpactWeigher(BaseEstimator, TransformerMixin):

    def __init__(self, w=1.0):
        self.w = w

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        vals = (X_.apply(self.__extract, axis=1, result_type='expand')
            .rename(columns={0:"from", 1:"to"})
            .apply(self.__parse, axis=1, result_type='expand')
            .rename(columns={0:"from", 1:"to"})
        )
        X_['from'] = vals['from']
        X_['to'] = vals['to']
        X['diff'] = X_.apply(self.__measure, axis=1)
        return X.drop('impact', axis=1)

    def __re_N(self, pat):
        return pat.replace('N', r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)%?')

    def __re_NP(self, pat):
        N = self.__re_N(r"((?:(?:\(N[\s\w']+\)|N\s*/|N)\s*[\-\+]?\s*)+)")
        return pat.replace('N', N)

    def __extract(self, row):
        text = row['text']
        impact = row['impact']
        if impact != -1 and impact != 1:
            return None, None

        if not re.search(self.__re_N('N'), text):
            return None, ""

        if re.search(self.__re_N(r'N.*? (?:from|instead of) .*?N'), text):
            m = re.search(self.__re_NP(r'N.*? (?:from|instead of) .*?N'), text)
            return m.groups()[::-1]

        if re.search(self.__re_N(r' from .*?N.*? to .*?N'), text):
            m = re.search(self.__re_NP(r' from .*?N.*? to .*?N'), text)
            return m.groups()

        return None, ""

    def __parse(self, row):
        val_from, val_to = row['from'], row['to']
        if val_from is None:
            return val_from, val_to
        return self.__parse_str(val_from), self.__parse_str(val_to)

    def __parse_str(self, s):
        return list(map(self.__parse_part, s.split('+')))

    def __parse_part(self, s):
        if ' x ' in s:
            return 'mul', self.__float(re.search(self.__re_N('N'), s).group(0))
        if (m := re.search(self.__re_N(r"^\s*[\(\)]*(N)\s\w[\s\w']*[\(\)]*\s*$"), s)):
            return 'scl', self.__float(m.group(1))
        return 'val', [self.__float(m) for m in re.findall(self.__re_N('N'), s)]

    def __float(self, s):
        s = s.strip()
        if s.endswith('%'):
            s = s[:-1]
        return float(s)

    def __measure(self, row):
        val_from, val_to = row['from'], row['to']
        text = row['text']
        impact = row['impact']
        if val_from is None:
            return self.__measure_no_number(impact, text)
        d = self.__measure_number(val_from, val_to)
        return impact * d

    def __measure_no_number(self, impact, text):
        m = 1
        if re.search(r'no longer|removed:|removed effect:', text, re.I):
            m = -1
        return self.w * impact * m

    def __measure_number(self, a_, b_):
        ts = ('val', 'scl', 'mul')
        a = {t: [v for k, v in a_ if k == t] for t in ts}
        b = {t: [v for k, v in b_ if k == t] for t in ts}
        a['val'] = self.__merge_vals(a['val'])
        b['val'] = self.__merge_vals(b['val'])
        zips = (
            self.__unaligned_zip(a['val'], b['val']),
            self.__exceeding_zip(a['scl'], b['scl']),
            self.__exceeding_zip(a['mul'], b['mul'])
        )
        diffs = list(chain.from_iterable(
            (b-a for a, b in self.__normalize_ts(z)) for z in zips
        ))
        return self.__normalize(reduce(lambda a,b:a+b, diffs, 0) / len(diffs))

    def __normalize_ts(self, v):
        v = list(v)
        if not v:
            return v
        m = min(min(abs(a), abs(b)) for a, b in v)
        e = 10 ** floor(log10(m)) if m > 0 else 1
        return ((a/e, b/e) for a, b in v)

    def __normalize(self, x):
        m = abs(x)
        e = 10 ** floor(log10(m)) if m > 0 else 1
        return x / e

    def __merge_vals(self, vals):
        def merge(acc, val):
            return [a + b for a, b in self.__unaligned_zip(acc, val or [0])]
        return reduce(merge, vals, [0])

    def __unaligned_zip(self, a, b):
        la, lb = len(a), len(b)
        if la == lb:
            yield from zip(a, b)
            return
        flipped = False
        if la > lb:
            la, lb = lb, la
            a, b = b, a
            flipped = True
        for i, bx in enumerate(b):
            i_ = floor(((i + 1) / lb) * la)
            i = floor((i / lb) * la)
            ax = (a[i] + a[i_]) / 2 if i_ < la else a[i]
            if flipped:
                yield bx, ax
            else:
                yield ax, bx

    def __exceeding_zip(self, a, b):
        la, lb = len(a), len(b)
        if la == lb:
            yield from zip(a, b)
            return
        flipped = False
        if la > lb:
            la, lb = lb, la
            a, b = b, a
            flipped = True
        for i, bx in enumerate(b):
            ax = a[i] if i < la else 0
            if flipped:
                yield bx, ax
            else:
                yield ax, bx
