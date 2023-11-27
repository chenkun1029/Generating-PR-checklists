import csv
import pandas as pd


# read csv file
def read_csv(path):
    with open(path, "rt", encoding="utf-8") as vsvfile:
        reader = csv.reader(vsvfile)
        res = [row for row in reader]
    return res[1:]


# drop duplicates
def duplicates(file_in, file_out):
    frame = pd.read_csv(file_in)
    data = frame.drop_duplicates(subset=None, keep='first', inplace=False)
    data.to_csv(file_out, index=False, encoding='utf8')


def func(file_in, file_out):
    # sort by forks
    df = pd.read_csv(file_in)
    df.sort_values("forks", ascending=False, inplace=True)

    # select specific index and drop
    row_indexs = df[pd.isnull(df['con'])].index
    row_indexs = df[df['forks'] < 1000].index
    df.drop(row_indexs, inplace=True)

    df.to_csv(file_out, index=False, encoding='utf8')


if __name__ == '__main__':
    df = pd.read_csv("./repo1.csv")
    df.sort_values("pr_count", ascending=False, inplace=True)
    df.to_csv("./repo2.csv", index=False, encoding='utf8')
    column_name = ['name', 'forks', 'stars', 'language', 'pr_count', 'con', 'prt']
    pd.DataFrame(columns=column_name).to_csv('./repo3.csv', index=False, encoding='utf-8')
    res = read_csv("./repo2.csv")
    for item in res:
        if "learn-co-" not in item[0]:
            pd.DataFrame(data=[item]).to_csv('./repo3.csv', mode='a+', index=False, header=False, encoding='utf-8')


