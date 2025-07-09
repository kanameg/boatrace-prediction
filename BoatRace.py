import json
import os
import pickle
import re
from datetime import date, timedelta

import pandas as pd


class BoatRace:
    def __init__(self, race_year: int, race_month: int, race_day: int) -> None:
        """initialize

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
        self : ScrapeRace
            ScrapeRace instance
        """
        self.year = race_year
        self.month = race_month
        self.day = race_day
        # load cource info form json file
        self.cources = self.load_course()
        self.races = self.load_races()

    def load_course(self) -> dict:
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
        file_name = "cource.json"
        with open(dir_path + file_name, "r") as f:
            cource = json.load(f)

        return cource

    # def load_pickle(self, race_year: int, race_month: int, race_day: int) -> dict:
    def load_pickle(self) -> dict:
        """load race result data from pickle file

        Parameters
        ----------
        None

        Returns
        -------
        results : dict

        """
        dir_path = "/workspace/data/pickle/"
        file_namme = f"race-{self.year:04}-{self.month:02}-{self.day:02}.pkl"
        with open(dir_path + file_namme, "rb") as f:
            results = pickle.load(f)

        return results

    def extract_racer_info(self, line: str) -> dict:
        """extract infomation from racer line to infomation dict

        Parameters
        ----------
        line : str
            racer line e.g "04   01  4 3930 岸　本　　　　隆 39   47    6.80   4    0.09     1.48.6"

        Returns
        -------
        racer_info : dict
            racer infomation dict
        """
        # ----- 結果抽出 -----
        decision = line[2:4].strip()
        rank = self.rank_str_to_rank(decision)
        color = int(line[5:7].strip())
        racer_id = int(line[8:12].strip())
        # racer_name = line[13:21].replace("　", "").strip()  # racer name is unused
        motor_number = int(line[22:24].strip())
        boat_number = int(line[27:29].strip())
        time_str = re.sub(r"\s|K|L", "", line[32:37].strip())  # exhibition time
        exhibition_time = self.time_str_to_sec(time_str, 2)
        approach_rank_str = line[39:41].strip()
        approach_rank = self.rank_str_to_rank(approach_rank_str)
        time_str = re.sub(
            r"\s|K|L", "", line[44:49].replace("F", "-").strip()
        )  # start timing
        start_time = self.time_str_to_sec(time_str, 2)
        time_str = re.sub(r"\s|K", "", line[53:60].strip())  # race time
        race_time = self.time_str_to_sec(time_str, 3)

        racer_info = {
            "rank": rank,
            "decision": decision,
            "color": color,
            "racer_id": racer_id,
            "motor_number": motor_number,
            "boat_number": boat_number,
            "exhibition_time": exhibition_time,
            "approach_rank": approach_rank,
            "start_time": start_time,
            "race_time": race_time,
        }

        return racer_info

    def extract_race_info(self, line: str) -> dict:
        """extracet race infomation form race line to dict

        Parameters
        ----------
        line : str
            race line e.g. "00    2R       一般戦　　　                 H1800m  晴　    風  北　　  1m波    1cm"

        Returns
        -------
        race_info : dict
            race infomation dict
        """
        line = line[:18] + line[18:].replace("進入固定", "        ")  # remove "進入固定"

        # ----- 情報抽出 -----
        race_number = int(line[2:4].strip())
        distance = int(line[36:40].strip())
        weather = line[43:45].strip()
        wind_direction = line[52:55].strip()
        wind_speed = int(line[56:58].strip())
        wave_height = int(line[63:65].strip())
        race_info = {
            "race_number": race_number,
            "distance": distance,
            "weather": weather,
            "wind_direction": wind_direction,
            "wind_speed": wind_speed,
            "wave_height": wave_height,
        }

        return race_info

    def load_races(self):
        races = []

        results = self.load_pickle()
        for cource in self.cources:
            cource_id, cource_name = cource["id"], cource["name"]
            courcae_races = results[cource_name]["races"]
            for courcae_race in courcae_races:
                race_lines = courcae_race.splitlines()
                race_number = int(race_lines[0].split()[0][:-1])
                race_info = self.extract_race_info(race_lines[0])
                for line in race_lines[4:10]:
                    racer_info = self.extract_racer_info(line)
                    racer_info["year"] = self.year
                    racer_info["month"] = self.month
                    racer_info["day"] = self.day
                    racer_info["cource_id"] = cource_id
                    # racer_info = dict(**racer_info, **race_info)
                    racer_info = racer_info | race_info
                    races.append(racer_info)
        self.races = races

        return races

    def to_dataframe(self) -> pd.DataFrame:
        """Dict to Pandas dataframe

        Parameters
        ----------
        None

        Returns
        -------
        df : pd.DataFrame
            Pandas dataframe
        """
        df = pd.DataFrame(self.races)
        return df

    def to_csv(self, file_name: str) -> None:
        """save dataframe to csv file

        Parameters
        ----------
        file_name : str
            csv file name

        Returns
        -------
        None
        """
        df = self.to_dataframe()
        df.to_csv(file_name, index=False)

    def time_str_to_sec(self, time_str: str, digits=3) -> float:
        """convert time string to second

        Parameters
        ----------
        time_str : str
            time string e.g. 1.23.45 or 23.45

        Returns
        -------
        second : float
            time to second
        """
        if time_str[0] == "-":
            sign = -1
        else:
            sign = 1

        if digits == 2:
            sec_str, msec_str = time_str.replace(" ", "").split(".")
            min_str = ""
        else:
            min_str, sec_str, msec_str = time_str.replace(" ", "").split(".")

        min = 0 if min_str == "" else int(min_str)
        sec = 0 if sec_str == "" else int(sec_str)
        msec = 0 if msec_str == "" else int(msec_str)

        time = sign * round(min * 60 + sec + msec / 100, 2)
        return time

    def rank_str_to_rank(self, rank_str: str) -> int:
        """convert decision to rank

        Parameters
        ----------
        rank_str : str
            decision string e.g. 1着 or 2着

        Returns
        -------
        rank : int
            decision to rank
        """
        if (
            (rank_str == "")  # 空文字
            or (rank_str == "F")  # F:フライング
            or (rank_str == "L0")  # L:選手責任外の出遅れ
            or (rank_str == "L1")  # L:選手責任の出遅れ
            or (rank_str == "K0")  # K0:選手責任外の事前欠場
            or (rank_str == "K1")  # K1:選手責任の事前欠場
            or (rank_str == "S0")  # S0:選手責任外の失格
            or (rank_str == "S1")  # S1:選手責任の失格
            or (rank_str == "S2")  # S2:他艇妨害の失格
        ):
            rank = 0  # DNS or DNF, DQ is 0
        else:
            rank = int(rank_str)
        return rank


"""

"""

if __name__ == "__main__":
    # race_year = 2023
    # race_month = 3
    # race_day = 1
    # boatrace = BoatRace(race_year, race_month, race_day)
    # df = boatrace.to_dataframe()
    # print(df)

    current_date = start_date = date(2023, 1, 1)  # start date
    end_date = date(2024, 1, 1)  # end date
    file_year = current_date.year

    race_df = pd.DataFrame()
    while current_date < end_date:
        race_year = current_date.year
        race_month = current_date.month
        race_day = current_date.day

        boatrace = BoatRace(race_year, race_month, race_day)
        dir_path = "/workspace/data/csv/"
        csv_file_name = f"race-{race_year:04}-{race_month:02}-{race_day:02}.csv"
        boatrace.to_csv(dir_path + csv_file_name)

        df = boatrace.to_dataframe()
        race_df = pd.concat([race_df, df])

        current_date += timedelta(days=1)

    # write race result infomaion to csv file
    dir_path = "/workspace/data/raw/"
    file_name = f"race-{file_year}.csv"
    race_df.to_csv(os.path.join(dir_path, file_name), index=False)

    # read racer infomation from csv file
    dir_path = "/workspace/data/raw/"
    file_name = "racer-2023-10.csv"
    racer_df = pd.read_csv(os.path.join(dir_path, file_name))

    # join race and racer data
    print(set(race_df["racer_id"].unique()) - set(racer_df["racer_id"].unique()))
    race_df = pd.merge(race_df, racer_df, on="racer_id", how="left")

    # write all information to train csv file
    dir_path = "/workspace/data/raw/"
    file_name = "train.csv"
    race_df.to_csv(os.path.join(dir_path, file_name), index=False)
