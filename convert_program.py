#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
番組表データ変換プログラム

ボートレースの公式サイトが提供する番組表データを読み込み、
CSV形式の番組表データに変換する
"""

import csv
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


class ProgramConverter:
    def __init__(self):
        # レース場番号のマッピング
        self.track_mapping = {
            "桐生": "01",
            "戸田": "02",
            "江戸川": "03",
            "平和島": "04",
            "多摩川": "05",
            "浜名湖": "06",
            "蒲郡": "07",
            "常滑": "08",
            "津": "09",
            "三国": "10",
            "びわこ": "11",
            "住之江": "12",
            "尼崎": "13",
            "鳴門": "14",
            "丸亀": "15",
            "児島": "16",
            "宮島": "17",
            "徳山": "18",
            "下関": "19",
            "若松": "20",
            "芦屋": "21",
            "福岡": "22",
            "唐津": "23",
            "大村": "24",
        }

        # 出力CSVのヘッダー
        self.csv_headers = [
            "年",
            "月",
            "日",
            "レース場番号",
            "レース番号",
            "距離(m)",
            "投票締切時間",
        ]

        # 6艇分のカラムを追加
        for i in range(1, 7):
            boat_prefix = f"{i}艇_"
            self.csv_headers.extend(
                [
                    f"{boat_prefix}選手登番",
                    f"{boat_prefix}年齢",
                    f"{boat_prefix}支部",
                    f"{boat_prefix}体重",
                    f"{boat_prefix}級別",
                    f"{boat_prefix}全国勝率",
                    f"{boat_prefix}全国2連率",
                    f"{boat_prefix}当地勝率",
                    f"{boat_prefix}当地2連率",
                    f"{boat_prefix}モーター番号",
                    f"{boat_prefix}モーター2連率",
                    f"{boat_prefix}ボート番号",
                    f"{boat_prefix}ボート2連率",
                ]
            )

    def extract_track_number(self, text: str) -> Optional[str]:
        """レース場名からレース場番号を抽出"""
        for track_name, track_num in self.track_mapping.items():
            if track_name in text:
                return track_num
        return None

    def parse_time(self, time_str: str) -> str:
        """投票締切時間を解析してHH:MM形式に変換"""
        # 全角数字を半角に変換
        time_str = time_str.translate(
            str.maketrans("０１２３４５６７８９：", "0123456789:")
        )

        # 時間パターンをマッチ
        pattern = r"(\d{1,2})[：:](\d{2})"
        match = re.search(pattern, time_str)
        if match:
            hour = match.group(1).zfill(2)
            minute = match.group(2)
            return f"{hour}:{minute}"
        return ""

    def parse_boat_data(self, line: str) -> Optional[Dict]:
        """艇の情報を固定位置で直接抽出"""
        # 行の長さをチェック（最低限ボート2連率まで取得できる長さ）
        if len(line) < 58:
            return None

        # 区切り線やヘッダー行を除外
        line_stripped = line.strip()
        if (
            line_stripped.startswith("-")
            or "選手" in line_stripped
            or "登番" in line_stripped
            or "番号" in line_stripped
        ):
            return None

        try:
            # 艇番（最初の1文字）
            boat_number = line[0:1].strip()

            # 艇番が数字でない場合は無効
            if not boat_number.isdigit():
                return None

            # 選手情報を固定位置で直接抽出
            player_id = line[2:6].strip()  # 選手登番
            player_name = line[6:10].strip()  # 選手名
            age = line[10:12].strip()  # 年齢
            branch = line[12:14].strip()  # 支部
            weight = line[14:16].strip()  # 体重
            player_class = line[16:18].strip()  # 級別

            # 選手登番が4桁の数字でない場合は無効
            if not (player_id.isdigit() and len(player_id) == 4):
                return None

            # 固定位置での数値抽出
            national_win_rate = line[19:23].strip()
            national_2nd_rate = line[24:29].strip()
            local_win_rate = line[30:34].strip()
            local_2nd_rate = line[35:40].strip()
            motor_number = line[41:43].strip()
            motor_2nd_rate = line[44:49].strip()
            boat_number_actual = line[50:52].strip()
            boat_2nd_rate = line[53:58].strip() if len(line) >= 58 else ""

            return {
                "boat_number": boat_number,
                "player_id": player_id,
                "player_name": player_name,
                "age": age,
                "branch": branch,
                "weight": weight,
                "class": player_class,
                "national_win_rate": national_win_rate,
                "national_2nd_rate": national_2nd_rate,
                "local_win_rate": local_win_rate,
                "local_2nd_rate": local_2nd_rate,
                "motor_number": motor_number,
                "motor_2nd_rate": motor_2nd_rate,
                "boat_number_actual": boat_number_actual,
                "boat_2nd_rate": boat_2nd_rate,
            }

        except (IndexError, ValueError):
            return None

    def parse_race_header(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """レースヘッダー情報を解析"""
        # 全角数字を半角に変換
        converted_line = line.translate(
            str.maketrans("０１２３４５６７８９Ｒ", "0123456789R")
        )

        # レース番号を抽出（全角・半角両対応）
        race_match = re.search(r"(\d{1,2})R", converted_line)
        if not race_match:
            # 全角数字のRパターンも試す
            race_match = re.search(r"[　\s]*([０１２３４５６７８９]+)[Ｒ]", line)
            if race_match:
                # 全角数字を半角に変換
                race_number = race_match.group(1).translate(
                    str.maketrans("０１２３４５６７８９", "0123456789")
                )
            else:
                return None
        else:
            race_number = race_match.group(1)

        # 距離を抽出（H1800m形式）
        distance_match = re.search(r"[HＨ](\d+)[mｍ]", converted_line)
        distance = distance_match.group(1) if distance_match else ""

        # 投票締切時間を抽出
        time = self.parse_time(line)

        # レース名はデフォルト値
        race_name = "予選"

        return race_number, race_name, distance, time

    def process_race_section(self, lines: List[str], start_idx: int) -> Optional[Dict]:
        """レース区間を処理"""
        race_data = None
        boats = {}

        i = start_idx
        while i < len(lines):
            line = lines[i].strip()

            # 次のレースの開始または区間終了
            if re.match(r".*\d+Ｒ.*", line) and i > start_idx:
                break
            if line.startswith("BEND") or line.startswith("FINALB"):
                break

            # レースヘッダーの解析
            if ("Ｒ" in line or "R" in line) and "電話投票締切予定" in line:
                race_info = self.parse_race_header(line)
                if race_info:
                    race_number, race_name, distance, time = race_info
                    race_data = {
                        "race_number": race_number,
                        "race_name": race_name,
                        "distance": distance,
                        "time": time,
                    }

            # 艇データの解析
            boat_data = self.parse_boat_data(line)
            if boat_data:
                boats[boat_data["boat_number"]] = boat_data

            i += 1

        if race_data and len(boats) >= 6:  # 6艇すべてのデータがある場合
            race_data["boats"] = boats
            return race_data

        return None

    def convert_file(self, year: int, month: int, day: int) -> int:
        """番組表ファイルを変換"""
        # ファイル名生成
        year_short = year % 100
        input_file = f"data/raw/programs/b{year_short:02d}{month:02d}{day:02d}_u8.txt"
        output_file = "data/race_programs.csv"

        if not os.path.exists(input_file):
            print(f"エラー: 入力ファイルが見つかりません: {input_file}")
            return 1

        try:
            # 入力ファイルを読み込み
            with open(input_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # データを解析
            races = []
            current_track_number = None

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # トラック開始マーカー
                if re.match(r"\d{2}BBGN", line):
                    track_num = line[:2]
                    current_track_number = track_num
                    i += 1
                    continue

                # レース場名からトラック番号を抽出（BBGNの次の行で）
                if current_track_number is None and "ボートレース" in line:
                    extracted_track = self.extract_track_number(line)
                    if extracted_track:
                        current_track_number = extracted_track

                # トラック終了マーカー
                if re.match(r"\d{2}BEND", line):
                    current_track_number = None
                    i += 1
                    continue

                # レースヘッダーの検出
                if (
                    ("Ｒ" in line or "R" in line)
                    and "電話投票締切予定" in line
                    and current_track_number
                ):
                    race_data = self.process_race_section(lines, i)
                    if race_data:
                        race_data["track_number"] = current_track_number
                        race_data["year"] = year
                        race_data["month"] = month
                        race_data["day"] = day
                        races.append(race_data)

                i += 1

            # CSVファイルに出力
            file_exists = os.path.exists(output_file)

            with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # ヘッダーを書き込み（ファイルが新規作成の場合）
                if not file_exists:
                    writer.writerow(self.csv_headers)

                # データを書き込み
                for race in races:
                    row = [
                        race["year"],
                        race["month"],
                        race["day"],
                        race["track_number"],
                        race["race_number"],
                        race["distance"],
                        race["time"],
                    ]

                    # 6艇分のデータを追加
                    for boat_num in range(1, 7):
                        boat_key = str(boat_num)
                        if boat_key in race["boats"]:
                            boat = race["boats"][boat_key]
                            row.extend(
                                [
                                    boat["player_id"],
                                    boat["age"],
                                    boat["branch"],
                                    boat["weight"],
                                    boat["class"],
                                    boat["national_win_rate"],
                                    boat["national_2nd_rate"],
                                    boat["local_win_rate"],
                                    boat["local_2nd_rate"],
                                    boat["motor_number"],
                                    boat["motor_2nd_rate"],
                                    boat["boat_number_actual"],
                                    boat["boat_2nd_rate"],
                                ]
                            )
                        else:
                            # データがない場合は空文字で埋める
                            row.extend([""] * 12)

                    writer.writerow(row)

            print(f"処理完了: {len(races)}レースのデータを変換しました")
            print(f"出力ファイル: {output_file}")
            return 0

        except Exception as e:
            print(f"エラー: ファイル処理中にエラーが発生しました: {e}")
            return 1


def main():
    """メイン関数"""
    if len(sys.argv) != 4:
        print("使用方法: python convert_program.py YYYY MM DD")
        print("  YYYY: 年4桁（例: 2025）")
        print("  MM: 1桁または2桁の月（例: 7）")
        print("  DD: 1桁または2桁の日（例: 9）")
        return 1

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])

        # 引数の妥当性チェック
        if not (1900 <= year <= 2100):
            print(f"エラー: 年は1900〜2100の範囲で入力してください: {year}")
            return 1

        if not (1 <= month <= 12):
            print(f"エラー: 月は1〜12の範囲で入力してください: {month}")
            return 1

        if not (1 <= day <= 31):
            print(f"エラー: 日は1〜31の範囲で入力してください: {day}")
            return 1

        # 出力ディレクトリの作成
        os.makedirs("data", exist_ok=True)

        # 変換処理実行
        converter = ProgramConverter()
        return converter.convert_file(year, month, day)

    except ValueError:
        print("エラー: 引数は数値で入力してください")
        return 1
    except Exception as e:
        print(f"エラー: 予期しないエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
