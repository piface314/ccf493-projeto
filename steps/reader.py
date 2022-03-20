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
            df = pd.DataFrame(data, columns=("patch", "date", "champion", "about", "text"))
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

    def __init__(self, fp):
        self.fp = fp

    def to_df(self):
        with jsonlines.open(self.fp) as reader:
            data = chain.from_iterable([(champ['champion'], *t) for t in self.parse_champion(champ)]
                for champ in reader)
            df = pd.DataFrame(data, columns=("champion", "date", "popularity", "winrate", "banrate"))
            return df

    def to_dict(self):
        with jsonlines.open(self.fp) as reader:
            data = {champ['champion']: list(self.parse_champion(champ))
                for champ in reader}
            return data

    def parse_champion(self, champion):
        cols = (self.parse_history(champion[col], i==0)
            for i, col in enumerate(["popularity", "winrate", "banrate"]))
        return ((pop[0], pop[1], win, ban) for pop, win, ban in zip(*cols))

    def parse_history(self, history, with_date=False):
        if with_date:
            return ((datetime.fromisoformat(t), x/100) for t, x in history)
        else:
            return (x/100 for _, x in history)

class ReleaseReader:

    def __init__(self, fp):
        self.fp = fp

    def to_df(self):
        df = pd.read_csv(self.fp)
        df['release'] = pd.to_datetime(df['release'])
        return df

    def to_dict(self):
        df = self.to_df()
        return {row['champion']: row['release'] for _, row in df.iterrows()}
