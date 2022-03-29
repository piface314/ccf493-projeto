from datetime import datetime
from itertools import chain
import jsonlines
import pandas as pd


class PatchHistoryReader:

    @classmethod
    def from_gbq(cls, credentials, pid='lol-patch-predict'):
        return pd.read_gbq(f'''SELECT * FROM {pid}.bd.patch''',
            project_id=pid,
            credentials=credentials)

    @classmethod
    def from_jsonl(cls, fp):
        with jsonlines.open(fp) as reader:
            data = chain.from_iterable(map(cls.parse_patch, reader))
            df = pd.DataFrame(data, columns=("patch", "date", "champion", "about", "text"))
            return df

    @classmethod
    def parse_patch(cls, obj):
        patch_id = obj['id']
        patch_date = datetime.fromisoformat(obj['date']) if obj['date'] else None
        champions = chain.from_iterable(map(cls.parse_champ, obj['champions']))
        return [(patch_id, patch_date, *c) for c in champions]

    @classmethod
    def parse_champ(cls, champ):
        name = champ['name']
        changes = chain.from_iterable(map(cls.parse_change, champ['changes']))
        return [(name, *c) for c in changes]

    @classmethod
    def parse_change(cls, change):
        if type(change) is str:
            return [(None, change)]
        about = change['about']
        return [(about, line) for line in change['lines']]

class PlayHistoryReader:

    @classmethod
    def from_gbq(cls, credentials, pid='lol-patch-predict'):
        return pd.read_gbq(f'''SELECT * FROM {pid}.bd.play_history''',
            project_id=pid,
            credentials=credentials)

    @classmethod
    def from_jsonl(cls, fp):
        with jsonlines.open(fp) as reader:
            data = chain.from_iterable([(champ['champion'], *t) for t in cls.parse_champion(champ)]
                for champ in reader)
            df = pd.DataFrame(data, columns=("champion", "date", "popularity", "winrate", "banrate"))
            return df

    @classmethod
    def parse_champion(cls, champion):
        cols = (cls.parse_history(champion[col], i==0)
            for i, col in enumerate(["popularity", "winrate", "banrate"]))
        return ((pop[0], pop[1], win, ban) for pop, win, ban in zip(*cols))

    @classmethod
    def parse_history(cls, history, with_date=False):
        if with_date:
            return ((datetime.fromisoformat(t), x/100) for t, x in history)
        else:
            return (x/100 for _, x in history)

class ReleaseReader:

    @classmethod
    def from_gbq(cls, credentials, data='champion', pid='lol-patch-predict', as_dict=False):
        df = pd.read_gbq(f'''SELECT * FROM {pid}.bd.{data}''',
            project_id=pid,
            credentials=credentials)
        return cls.as_dict(df) if as_dict else df

    @classmethod
    def from_csv(cls, fp, as_dict=False):
        df = pd.read_csv(fp)
        df['release'] = pd.to_datetime(df['release'])
        return cls.as_dict(df) if as_dict else df

    @classmethod
    def as_dict(cls, df):
        return {row['champion']: row['release'] for _, row in df.iterrows()}
