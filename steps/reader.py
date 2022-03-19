from datetime import datetime
from itertools import chain
import jsonlines
import pandas as pd


class PatchHistoryReader:

    def __init__(self, fp):
        self.fp = fp

    def to_df(self):
        with jsonlines.open(self.fp) as reader:
            data = chain.from_iterable(map(self.parse_patch, reader))
            df = pd.DataFrame(data, columns=(
                "patch", "date", "champion", "about", "text"))
            return df

    def parse_patch(self, obj):
        patch_id = obj['id']
        patch_date = datetime.fromisoformat(obj['date']) if obj['date'] else None
        champions = chain.from_iterable(map(self.parse_champ, obj['champions']))
        return [(patch_id, patch_date, *c) for c in champions]

    def parse_champ(self, champ):
        name = champ['name']
        changes = chain.from_iterable(map(self.parse_change, champ['changes']))
        return [(name, *c) for c in changes]

    def parse_change(self, change):
        if type(change) is str:
            return [(None, change)]
        about = change['about']
        return [(about, line) for line in change['lines']]

class PlayHistoryReader:

    pass

class ReleaseReader:

    def __init__(self, fp):
        self.fp = fp

    def to_df(self):
        df = pd.read_csv(self.fp)
        df['release'] = pd.to_datetime(df['release'])
        return df

    def to_dict(self):
        df = self.to_df()
        cols = set(df.columns) - {'champion'}
        if len(cols) > 1:
            return {row['champion']: {k: v for k, v in row.items() if k in cols}
                for _, row in df.iterrows()}
        else:
            return {row['champion']: row['release'] for _, row in df.iterrows()}
