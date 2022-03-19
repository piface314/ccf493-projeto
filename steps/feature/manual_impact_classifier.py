from steps.reader import PatchHistoryReader
import json
import pandas as pd
import re

class ManualImpactClassifier:

    keymap = {
        'p':  1,  # positive/direct
        'n': -1,  # negative/inverse
        'b':  0,  # bugfix
        'x': -2   # discard/irrelevant
    }

    def __init__(self, patches_df, filters_fp):
        self.patches_df = patches_df[["champion", "about", "text"]]
        self.filters_fp = filters_fp
        try:
            self.filters = json.load(open(filters_fp))
        except:
            self.filters = {
                'specific': [],
                'patterns': [[r'^bug\s*fix', 0], [r'^fix', 0]]
            }


    def apply_patterns(self, t):
        for pattern, impact in self.filters['patterns']:
            if re.search(pattern, t, re.IGNORECASE):
                return impact
        return None


    def multispec(self, df: pd.DataFrame, specific):
        for i, row in df.iterrows():
            try:
                print(f"Champion: {row['champion']}, about: {row['about']}")
                print(row['text'])
                key, = re.search("^\s*(\w)", input(">>> ")).groups()
                specific.append((int(i), self.keymap[key]))
            except Exception as e:
                print(e)
                break


    def classify(self):
        df = self.patches_df
        df_ = df.copy()
        change = True
        patterns = self.filters['patterns']
        specific = self.filters['specific']
        try:
            while True:
                if change:
                    df_['impact'] = df_['text'].map(self.apply_patterns)
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
                    patterns.append((arg[2:], self.keymap[arg[0]]))
                    print(patterns)
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
                    specific.append((int(i), self.keymap[key]))
                    change = True
                elif cmd == 'ii':
                    i = df_show.head(1).index[0]
                    specific.append((int(i), self.keymap[arg[0]]))
                    change = True
                elif cmd == 'm':
                    self.multispec(df_show, specific)
                    change = True
        except EOFError:
            print()
        except Exception as e:
            print(e)
        finally:
            json.dump(self.filters, open(self.filters_fp, 'w'))
            print(self.filters)
            return df_


if __name__ == '__main__':
    df = PatchHistoryReader('data/patches.jsonl').to_df()
    clf = ManualImpactClassifier(df, 'data/filters.json')
    df_ = clf.classify()
    df_.to_csv(f'data/impact.csv', index=False)
