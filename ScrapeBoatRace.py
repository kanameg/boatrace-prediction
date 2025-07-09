# -------------------------------------------------------------------
# ライブラリの読込
# -------------------------------------------------------------------
import json
import pickle
from datetime import date, datetime, timedelta
from time import sleep

import requests
from bs4 import BeautifulSoup
from matplotlib.pylab import f

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


class ScrapeBoatRace:
    """
    Attributes:
    ----------

    """

    results = {}
    cource_info = {}

    def __init__(self) -> None:
        """initialize
        Parameters
        ----------
        None

        Returns
        -------
        self : ScrapeRace
            ScrapeRace instance
        """
        pass

    def cource_info(self):
        """read cource number info from cource.json to dict
        It will be classified as BoatRaceCourse class in the future.

        Parameters
        ----------
        None

        Returns
        -------
        cource_info : dict
            cource info dict
        """
        dir_path = "/workspace/data/"
        file_name = "cource_num.json"
        with open(dir_path + file_name, "r") as f:
            cource_info = json.load(f)

        return cource_info

    def race_results_course(
        self, race_year: int, race_month: int, race_day: int, cource_num: int
    ) -> dict:
        """Scraping race results of the cource number from mbrace.or.jp

        https://www1.mbrace.or.jp/od2/K/pindex.html

        Parameters
        ----------
        course_num : int
            course number e.g. 20

        Returns
        -------
        results : dict
            dict of race result text

        """
        requests_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        requests_header = {"User-Agent": requests_user_agent}

        base_url = "https://www1.mbrace.or.jp/od2/K"  # base URL
        url = f"{base_url}/{race_year:04}{race_month:02}/{cource_num:02}/{race_day:02}.html"
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
        results = {"tournament": tournament, "races": races}

        return results

    def race_results(self, race_year: int, race_month: int, race_day: int) -> dict:
        """scrape race result of all cource

        ----------
        Parameters
        ----------
        race_year : int
            race year e.g. 2021
        race_month : int
            race month e.g. 1
        race_day : int
            race day e.g. 31
        race_cource : int
            race cource number e.g. 20


        Returns
        -------
        results : dict

        """
        cource = self.cource_info()
        cource_names = list(cource.keys())

        results = {}
        for cource_name in cource_names:
            race_cource_num = cource[cource_name]
            cource_results = self.race_results_course(
                race_year, race_month, race_day, race_cource_num
            )
            # print cource result
            print(f"{race_year:04}年{race_month:02}月{race_day:02}日 ", end="")
            if races := cource_results["races"]:
                print(GREEN + f"{cource_name}競艇場の{len(races)}レース分の結果を取得しました" + END)
            else:
                print(RED + f"{cource_name}競艇場は開催されていません" + END)
            results[cource_name] = cource_results

        self.results = results
        return results

    def write_results_pickle(
        self, race_year: int, race_month: int, race_day: int, results: dict = None
    ) -> None:
        """write race result text to pickle file

        Parameters
        ----------
        results : dict

        Returns
        -------
        None

        """
        if results is None:
            results = self.results

        dir_path = "/workspace/data/raw/"
        file_name = f"race-{race_year:04}-{race_month:02}-{race_day:02}.pkl"
        with open(dir_path + file_name, "wb") as f:
            pickle.dump(results, f)


if __name__ == "__main__":
    current_date = start_date = date(2023, 11, 1)  # start date
    end_date = date(2024, 1, 1)  # end date

    while current_date < end_date:
        race_year = current_date.year
        race_month = current_date.month
        race_day = current_date.day

        scrape = ScrapeBoatRace()
        results = scrape.race_results(race_year, race_month, race_day)
        scrape.write_results_pickle(race_year, race_month, race_day, results)

        # # read pickle file and print
        # dir_path = "/workspace/data/raw/"
        # file_name = f"race-{race_year:04}-{race_month:02}-{race_day:02}.pkl"
        # with open(dir_path + file_name, "rb") as f:
        #     f_results = pickle.load(f)

        # for cource_name, results in f_results.items():
        #     print("-" * 100)
        #     print(f"🔹コース: {cource_name}")
        #     print(f"🔹大会:")
        #     tournament = results["tournament"]
        #     print(tournament)
        #     print(f"🔹レース結果:")
        #     races = results["races"]
        #     for race in races:
        #         print(race)

        current_date += timedelta(days=1)

"""
{
    "cource name": {
        "tournament": "tournament text",
        "races": [rece result text, ...],
    },
    ...
 }"
"""

# def get_race_info(race_text):
#     """ """
#     race_lines = race_text.splitlines()
#     rcae_number = int(race_lines[0].split()[0][:-1])  # race number

#     racers = race_lines[4:10]  # 6 racers
#     for racer in racers:
#         # ----- extract results -----
#         rank = racer[2:4].strip()
#         color = racer[5:7].strip()
#         racer_id = racer[8:12].strip()
#         racer_name = racer[13:21].replace("　", "").strip()
#         motor_number = racer[22:24].strip()
#         boat_number = racer[27:29].strip()
#         exhibition = racer[32:37].strip()
#         approach_rank = racer[39:41].strip()
#         start_timing = racer[44:49].replace("F", "-").strip()
#         race_time = racer[53:60].strip()
