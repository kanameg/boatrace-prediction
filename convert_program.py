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

    def parse_distance(self, distance_str: str) -> str:
        """距離を解析してメートル数を抽出"""
        # 全角数字を半角に変換
        distance_str = distance_str.translate(
            str.maketrans("０１２３４５６７８９", "0123456789")
        )

        # 数字のみを抽出
        pattern = r"(\d+)"
        match = re.search(pattern, distance_str)
        if match:
            return match.group(1)
        return ""

    def parse_boat_data(self, line: str) -> Optional[Dict]:
        """艇の情報を解析"""
        # 基本的な艇情報のパターン（100%や特殊ケースに対応）
        # 1 3501川上昇平54長崎55B1 4.92 25.30 5.38 33.85 50 30.22 12 36.62              8
        # 3 5128坪井爽佑27三重57B1 3.07 16.22 3.38 17.32 16  0.00 51100.00 611         12
        pattern = r"^(\d)\s+(\d+)([^\d]+?)(\d{2})([^\d]+?)(\d{2})([AB]\d)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)\s+([0-9.]+)\s+(\d+)\s*([0-9.]+)"

        match = re.match(pattern, line)
        if not match:
            return None

        return {
            "boat_number": match.group(1),
            "player_id": match.group(2),
            "player_name": match.group(3).strip(),
            "age": match.group(4),
            "branch": match.group(5).strip(),
            "weight": match.group(6),
            "class": match.group(7),
            "national_win_rate": match.group(8),
            "national_2nd_rate": match.group(9),
            "local_win_rate": match.group(10),
            "local_2nd_rate": match.group(11),
            "motor_number": match.group(12),
            "motor_2nd_rate": match.group(13),
            "boat_number_actual": match.group(14),
            "boat_2nd_rate": match.group(15),
        }

    def parse_race_header(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """レースヘッダー情報を解析"""
        # レース番号、レース名、距離、投票締切時間を抽出
        # 　１Ｒ  予選　　　　          Ｈ１８００ｍ  電話投票締切予定１７：４１
        # 　５Ｒ  ５ールドレー          Ｈ１２００ｍ  電話投票締切予定１２：２８
        # １２Ｒ  ツッキー選抜          Ｈ１２００ｍ  電話投票締切予定１６：１５

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
        if distance_match:
            distance = distance_match.group(1)
        else:
            distance = ""

        # 投票締切時間を抽出
        time = self.parse_time(line)

        # レース名を抽出（簡易版）
        race_name = "予選"  # デフォルト

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

            # レースヘッダーの解析（Ｒまたは R を含む行で、全角半角両対応）
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

                # レースヘッダーの検出（全角半角Rに対応し、より広範囲にマッチ）
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
