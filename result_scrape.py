import os
import pickle
import sys
from datetime import date
from getopt import getopt
from time import sleep

import lxml
import pandas as pd
import requests
from bs4 import BeautifulSoup

from config import config
from cources import cources

# -------------------------------------------------------------------
# Terminal Color of Escape Sequence
# -------------------------------------------------------------------
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"
UNDERLINE = "\033[4m"
BOLD = "\033[1m"
END = "\033[0m"


def scrape_results(year: int, month: int, day: int) -> dict:
    """scrape race programs of all cources

    Parameters
    ----------
    year : int
        race year e.g. 2021
    month : int
        race month e.g. 1
    day : int
        race day e.g. 31

    Returns
    -------
    results : dict
        race result at all cource

    """
    results = {}
    # cources = cources()  # load cource info
    for cource in cources:  # loop for all cource
        cource_id = cource["id"]
        cource_name = cource["name"]
        result = scrape_results_course(year, month, day, cource_id)
        # print scrape status
        print(f"{year:04}年{month:02}月{day:02}日 ", end="")
        if races := result["races"]:
            print(GREEN + f"{cource_name}競艇場の{len(races)}レース分の結果を取得しました" + END)
        else:
            print(RED + f"{cource_name}競艇場は開催されていません" + END)
        results[cource_name] = result

    return results


def scrape_results_course(year: int, month: int, day: int, cource_id: int) -> dict:
    """Scraping race results of the cource number from mbrace.or.jp

    https://www1.mbrace.or.jp/od2/K/pindex.html

    Parameters
    ----------
    course_num : int
        course number e.g. 20 for 唐津

    Returns
    -------
    results : dict
        dict of race result text

    """
    requests_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    requests_header = {"User-Agent": requests_user_agent}

    base_url = "https://www1.mbrace.or.jp/od2/K"  # base URL
    url = f"{base_url}/{year:04}{month:02}/{cource_id:02}/{day:02}.html"
    print(url)
    try:
        response = requests.get(url, headers=requests_header)
        sleep(2)
        response.encoding = "EUC-JP"
    except requests.exceptions.RequestException as e:
        print(f"requests error occur {e}")

    soup = BeautifulSoup(response.text, "lxml")

    if pres := soup.find_all("pre"):
        tournament = pres[0].text  # tournament text
        races = [pre.text for pre in pres[1:]]  # race results text
    else:
        # not held
        tournament = ""
        races = []
    result = {"tournament": tournament, "races": races}

    return result


def dump_results(results: dict, year: int, month: int, day: int) -> None:
    # pickle file name
    pickle_name = f"result-{year:04}-{month:02}-{day:02}.pkl"
    pickle_dir = os.path.join(config["dir"]["pickle"], "result")
    pickle_path = os.path.join(pickle_dir, pickle_name)

    # dump result dict to pickle file
    with open(pickle_path, "wb") as f:
        pickle.dump(results, f)


if __name__ == "__main__":
    try:
        opts, args = getopt(sys.argv[1:], "s:e:", ["start=", "end="])
    except getopt.GetoptError as e:
        print(e)
        sys.exit(2)
    print(opts)

    # Analyze command options list
    start = None
    end = None
    for opt, arg in opts:
        if opt in ("-s", "--start"):
            start = int(arg)
        elif opt in ("-e", "--end"):
            end = int(arg)

    if start is None:
        start = date.today().strftime("%Y%m%d")
    start_date = pd.to_datetime(start, format="%Y%m%d")

    if end is None:
        end = start
    end_date = pd.to_datetime(end, format="%Y%m%d")
    current_date = start_date

    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        day = current_date.day

        # scrape result
        results = scrape_results(year, month, day)

        # dump result
        dump_results(results, year, month, day)

        current_date = current_date + pd.Timedelta(days=1)
