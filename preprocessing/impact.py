import json
import pandas as pd
from itertools import chain
import jsonlines
from datetime import datetime
import re

def parse_change(change):
  if type(change) is str:
    return [(None, change)]
  about = change['about']
  return [(about, line) for line in change['lines']]

def parse_champ(champ):
  name = champ['name']
  changes = chain.from_iterable(map(parse_change, champ['changes']))
  return [(name, *c) for c in changes]

def parse_patch(obj):
  return chain.from_iterable(map(parse_champ, obj['champions']))

def to_df(fp):
  with jsonlines.open(fp) as reader:
    data = chain.from_iterable(map(parse_patch, reader))
    df = pd.DataFrame(data, columns=("champion", "about", "text"))
    return df

keymap = {
  'p': 1, # positive
  'n': -1, # negative
  'b': 0, # bugfix
  'x': -2 # discard
}

def apply_filters(filters):
  def _(t: str):
    for pattern, impact in filters:
      if re.search(pattern, t, re.IGNORECASE):
        return impact
    return None
  return _

def multispec(df: pd.DataFrame, specific):
  for i, row in df.iterrows():
    try:
      print(f"Champion: {row['champion']}, about: {row['about']}")
      print(row['text'])
      key, = re.search("^\s*(\w)", input(">>> ")).groups()
      specific.append((int(i), keymap[key]))
    except Exception as e:
      print(e)
      break
  
  

def classify(df: pd.DataFrame, filters_):
  df_ = df.copy()
  change = True
  specific = filters_['spec']
  filters = filters_['filters']
  try:
    while True:
      if change:
        df_['impact'] = df_['text'].map(apply_filters(filters))
        for i, val in specific:
          df_.at[i, 'impact'] = val
        df_show = df_[df_['impact'].isna()]
        print(df_show)
        change = False
      s = input(">>> ")
      cmd, arg = re.search("^\s*(\w+)\s*(.*)", s).groups()
      if cmd == 's' or cmd == 'search':
        print(arg)
        print(df_show[df_show['text'].map(lambda t: bool(re.search(arg, t, re.IGNORECASE)))])
      elif cmd == 'a' or cmd == 'add':
        filters.append((arg[2:], keymap[arg[0]]))
        print(filters)
        change = True
      elif cmd == 't' or cmd == 'text':
        if arg:
          row = df_.iloc[int(arg)]
        else:
          row = df_show.head(1).iloc[0]
        print(f"Champion: {row['champion']}, about: {row['about']}")
        print(row['text'])
      elif cmd == 'i':
        i, key = re.search(r'(\d+)\s+(.)', arg).groups()
        specific.append((int(i), keymap[key]))
        change = True
      elif cmd == 'ii':
        i = df_show.head(1).index[0]
        specific.append((int(i), keymap[arg[0]]))
        change = True
      elif cmd == 'm':
        multispec(df_show, specific)
        change = True
  except EOFError:
    print()
  print(filters_)
  df_ = df_[df_['impact'] != -2]
  return df_

if __name__ == '__main__':
  filters_fp = 'data/filters.json'
  df = to_df('data/patches.jsonl')
  try:
    filters = json.load(open(filters_fp))
  except:
    filters = [[r'^bug\s*fix', 0], [r'^fix', 0]]
  try:
    df_ = classify(df, filters)
  except Exception as e:
    print(e)
  finally:
    json.dump(filters, open(filters_fp, 'w'))
  now = str(datetime.now())[:19].replace(' ', '-')
  df_.to_csv(f'data/impact-{now}.csv')
