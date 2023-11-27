import re
import time
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import csv
import pandas as pd

header = {
    'token': '***',
    'User-Agent': '***',
    'Cookie': '***'
}


# read csv file
def read_csv(path):
    with open(path, "rt", encoding="utf-8") as vsvfile:
        reader = csv.reader(vsvfile)
        res = [row for row in reader]
    return res[1:]


# visit a html page
def pagevisit(url, headers):
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, features='html.parser')
    response.close()
    return soup


def get_con(soup):
    con = soup.find(name='a', text="Contributing")
    if con is None:
        return ''
    else:
        return con['href']


def get_prt(soup):
    prt = soup.find(name='a', text="Pull request template")
    if prt is None:
        return ''
    else:
        return prt['href']


def main(res, start_point):
    try:
        for i in range(start_point, len(res)):
            item = res[i]
            home_url = "https://github.com/" + item[0] + "/community"
            print(home_url)
            soup = pagevisit(home_url, header)
            time.sleep(2)
            item.append(get_con(soup))
            item.append(get_prt(soup))
            pd.DataFrame(data=[item]).to_csv("../repo1.csv", mode='a+', index=False, header=False, encoding='utf-8')
            print("Line {} Success".format(i))
    except urllib.error.HTTPError:
        return i + 1
    except Exception as err:
        print("ERROR info: " + str(re.sub(r':\s/[a-z]{5}/.*>', '', str(err))))
        print("Unknown Error in Line {}!!! retry in 10 seconds".format(i))
        time.sleep(10)
        return i


if __name__ == '__main__':
    column_name = ['name', 'forks', 'stars', 'language', 'pr_count', 'con', 'prt']
    pd.DataFrame(columns=column_name).to_csv("./repo1.csv", index=False, encoding='utf-8')
    Res = read_csv("../repo_count.csv")
    start_point = 0
    while start_point < len(Res):
        error_at = main(Res, start_point)
        start_point = error_at
