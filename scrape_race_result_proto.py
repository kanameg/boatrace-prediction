# -------------------------------------------------------------------
# ライブラリの読込
# -------------------------------------------------------------------
import csv

import requests
from bs4 import BeautifulSoup

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

# -------------------------------------------------------------------
# Lits of Cource name
# -------------------------------------------------------------------
cource_name = [
    "桐生",
    "戸田",
    "江戸川",
    "平和島",
    "多摩川",
    "浜名湖",
    "蒲郡",
    "常滑",
    "津",
    "三国",
    "びわこ",
    "住之江",
    "尼崎",
    "鳴門",
    "丸亀",
    "児島",
    "宮島",
    "徳山",
    "下関",
    "若松",
    "芦屋",
    "福岡",
    "唐津",
    "大村",
]


def scrape_rece_result(
    race_year: int, race_month: int, race_day: int, race_cource: int
):
    rae_date = f"{race_year:04}-{race_month:02}-{race_day:02}"


# -------------------------------------------------------------------
# コンペ実行フラグ
# -------------------------------------------------------------------
competition = False

# -------------------------------------------------------------------
# レース情報定義
# -------------------------------------------------------------------
race_year = 2025
race_month = 7
race_day = 1
race_date = "{:04}-{:02}-{:02}".format(race_year, race_month, race_day)

race_cource = 4  # 1:桐生  4:平和島
cource_name = [
    "桐生",
    "戸田",
    "江戸川",
    "平和島",
    "多摩川",
    "浜名湖",
    "蒲郡",
    "常滑",
    "津",
    "三国",
    "びわこ",
    "住之江",
    "尼崎",
    "鳴門",
    "丸亀",
    "児島",
    "宮島",
    "徳山",
    "下関",
    "若松",
    "芦屋",
    "福岡",
    "唐津",
    "大村",
]
race_cource_name = cource_name[race_cource - 1]

base_url_result = "https://www1.mbrace.or.jp/od2/K"  # レース結果のURLベース

# -------------------------------------------------------------------
# HTML取得
# -------------------------------------------------------------------
requests_user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
requests_header = {"User-Agent": requests_user_agent}
url = "{}/{:04}{:02}/{:02}/{:02}.html".format(
    base_url_result, race_year, race_month, race_cource, race_day
)
print(url)
try:
    res = requests.get(url, headers=requests_header)
    res.encoding = "EUC-JP"
    # res.encoding = res.apparent_encoding
except requests.exceptions.RequestException as e:
    print("requests error occur {}".format(e))

# print(res.text)
soup = BeautifulSoup(res.text, "lxml")


head_list = [
    "年月日",
    "競艇場番号",
    "競艇場",
    "レース",
    "着",
    "艇",
    "登番",
    "選手名",
    "モータ",
    "ボート",
    "展示",
    "進入",
    "スタートタイミング",
    "レースタイム",
]


"""
00    2R       一般戦　　　                 H1800m  晴　    風  北　　  1m波    1cm
01                                                    スタート   レース   決まり手
02   着 艇 登番   選  手  名  モータ ボート 展示 進入 タイミング タイム   恵まれ　　
03 --------------------------------------------------------------------
   00000000001111 1 1 1 1 1 1 2 22222222233333333334444444444555555555566666666667777777777
   01234567890123 4 5 6 7 8 9 0 12345678901234567890123456789012345678901234567890123456789
04   01  4 3930 岸　本　　　　隆 39   47    6.80   4    0.09     1.48.6
05   02  6 3352 小　川　　晃　司 41   41    6.83   6    0.04     1.50.2
06   03  3 4652 酒　見　　峻　介  2   66    6.72   3    0.01     1.50.6
07   04  5 4878 西　岡　　育　未 24   69    6.75   5    0.07     1.50.9
08   F   1 4204 柴　田　　大　輔 55   22    6.69   1   F0.01      .  . 
09   F   2 4734 安河内　　　　将 25   17    6.82   2   F0.01      .  . 

     01  5 4314 青　木　　幸太郎 56   11    6.77   4    0.13     1.48.7
     02  6 3919 村　上　　　　純 48   29    6.86   1    0.14     1.49.9
     03  3 3576 白　水　　勝　也 11   49    6.76   2    0.38     1.51.4
     04  2 3506 宮　西　　真　昭 33   75    6.77   3    0.23     1.52.9
     05  4 5192 中　尾　　優　香 16   44    6.73   5    0.08      .  . 
     K0  1 3986 沖　島　　広　和 52   61   K .         K .        .  . 
"""

input_path = "../data/raw/race_result/"
csv_filename = "result-{}-{}.csv".format(race_date, race_cource)

with open(input_path + csv_filename, "w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    # --------------------------------------
    # ヘッダ出力
    # --------------------------------------
    # print(head_list)
    csv_writer.writerow(head_list)
    races = [pre.text for pre in soup.find_all("pre")[1:]]
    for race in races:
        race_lines = race.splitlines()
        rcae_number = int(race_lines[0].split()[0][:-1])

        racers = race_lines[4:10]
        for racer in racers:
            # ----- 結果抽出 -----
            rank = racer[2:4].strip()
            color = racer[5:7].strip()
            racer_id = racer[8:12].strip()
            racer_name = racer[13:21].replace("　", "").strip()
            motor_number = racer[22:24].strip()
            boat_number = racer[27:29].strip()
            exhibition = racer[32:37].strip()
            approach_rank = racer[39:41].strip()
            start_timing = racer[44:49].replace("F", "-").strip()
            race_time = racer[53:60].strip()
            # rank = result[0]
            # color = int(result[1])
            # racer_id = int(result[2])
            # racer_name = result[3]
            # motor_number = int(result[4])
            # boat_number = int(result[5])
            # if rank[0] == 'K':
            #     # 欠場処理
            #     print(YELLOW + rank + ' ' + END, end="")
            #     exhibition = None
            #     approach_rank = None
            #     start_timing = None
            #     result[9] = '..'
            # elif rank[0] == 'L':
            #     # 出遅れ処理
            #     print(YELLOW + rank + ' ' + END, end="")
            #     exhibition = float(result[6])
            #     approach_rank = None
            #     start_timing = None
            #     result[9] = '..'
            # elif rank[0] == 'F':
            #     # フライング処理
            #     print(YELLOW + rank + ' ' + END, end="")
            #     exhibition = float(result[6])
            #     approach_rank = int(result[7])
            #     start_timing = float(result[8].replace('F', '-'))
            # else:
            #     exhibition = float(result[6])
            #     approach_rank = int(result[7])
            #     start_timing = float(result[8])

            # # 計測値なしの場合の処理
            # if len(result) == 11 and result[9] == '.' and result[10] == '.':
            #     result[9] = result[9]  + result[10]
            #     result = result[:10]
            # race_time = [int(t) if t else None for t in result[9].split('.')]
            # 成績リスト
            result_list = [
                race_date,
                race_cource,
                race_cource_name,
                rcae_number,
                rank,
                color,
                racer_id,
                racer_name,
                motor_number,
                boat_number,
                exhibition,
                approach_rank,
                start_timing,
                race_time,
            ]
            # --------------------------------------
            # 結果出力
            # --------------------------------------
            # print(result_list)
            csv_writer.writerow(result_list)
