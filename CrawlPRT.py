import re
import time
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import csv
import pandas as pd

header = {
    'token': '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',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36',
    'Cookie': '_ga=GA1.2.1604869179.1603094657; _device_id=50d772b98986ef33e94f97011945d14a; _octo=GH1.1.624612414.1634720273; tz=Asia%2FShanghai; user_session=eK3l0t_BYcPbRzEKfpLoAQEuu0SKOMVxJrXCFHXfLatmK11d; tz=Asia%2FShanghai; color_mode=%7B%22color_mode%22%3A%22light%22%2C%22light_theme%22%3A%7B%22name%22%3A%22light%22%2C%22color_mode%22%3A%22light%22%7D%2C%22dark_theme%22%3A%7B%22name%22%3A%22dark%22%2C%22color_mode%22%3A%22dark%22%7D%7D; logged_in=yes; dotcom_user=chenkun1029; has_recent_activity=1; _gh_sess=JbI1HiGnVjMeh1k6lI4S%2F2hEVKJVdJGaloP3D72bI9yfp3ExBQR88u3e%2BUdFGcwQvx0Pv%2F%2B6heCEpfqIq2dBIO02O30hmlJDZ7Khxr5j7pQy%2FJtlSzErVGYha9fBnb0UoGQYDPNSpDNPK27ymT1ouATHzV7t8nxFdyH5a4ZUI8krT8ZdzTNo02MIvFwVEhlF6hflZTfRaAl%2FaB1kkYavs1zPhMMDX2bbGD41NzL4rYOOd94omu40uGZIlYxyhsUmoxiTcbEEUrZ8qro1aJE1ZN3uL1N4aerq5RzhFA%3D%3D--aKkeQTG8DbZYktXQ--lNvhj1et4zKhmS1FndfDEA%3D%3D'
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
