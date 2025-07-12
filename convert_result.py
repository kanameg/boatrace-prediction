#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競走結果データ変換プログラム

ボートレースの公式サイトが提供する競走結果データを読み込み、
CSV形式の競走結果データに変換する
"""

import csv
import os
import re
import sys
from typing import Dict, List, Optional, Tuple


class ResultConverter:
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
            "天候",
            "風向",
            "風速(m)",
            "波高(cm)",
            "単勝_艇番",
            "単勝_払戻金",
            "複勝1着_艇番",
            "複勝1着_払戻金",
            "複勝2着_艇番",
            "複勝2着_払戻金",
            "2連単_艇番",
            "2連単_払戻金",
            "2連単_人気",
            "2連複_艇番",
            "2連複_払戻金",
            "2連複_人気",
            "拡連複1_艇番",
            "拡連複1_払戻金",
            "拡連複1_人気",
            "拡連複2_艇番",
            "拡連複2_払戻金",
            "拡連複2_人気",
            "拡連複3_艇番",
            "拡連複3_払戻金",
            "拡連複3_人気",
            "3連単_艇番",
            "3連単_払戻金",
            "3連単_人気",
            "3連複_艇番",
            "3連複_払戻金",
            "3連複_人気",
        ]

        # 6艇分のレース結果カラムを追加
        for i in range(1, 7):
            boat_prefix = f"{i}艇_"
            self.csv_headers.extend(
                [
                    f"{boat_prefix}着順",
                    f"{boat_prefix}選手登番",
                    f"{boat_prefix}艇番",
                    f"{boat_prefix}モーター番号",
                    f"{boat_prefix}ボート番号",
                    f"{boat_prefix}展示",
                    f"{boat_prefix}進入",
                    f"{boat_prefix}スタートタイミング",
                    f"{boat_prefix}レースタイム",
                ]
            )

    def extract_track_number(self, text: str) -> Optional[str]:
        """レース場名からレース場番号を抽出"""
        for track_name, track_num in self.track_mapping.items():
            if track_name in text:
                return track_num
        return None

    def parse_betting_results_in_race(
        self, lines: List[str], start_idx: int
    ) -> Dict[str, Dict]:
        """レース内の払戻金情報を解析"""
        betting_results = {}

        i = start_idx
        while i < len(lines):
            line = lines[i].strip()

            # 次のレースの開始で終了
            if re.search(r"^\s+\d+R\s+", line) and i > start_idx:
                break

            # 空行をスキップ
            if not line:
                i += 1
                continue

            # 各賭け式の解析
            if "単勝" in line:
                # 単勝     1          130
                match = re.search(r"単勝\s+(\d+)\s+(\d+)", line)
                if match:
                    betting_results["単勝"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                    }

            elif "複勝" in line:
                # 複勝     1          140  3          290
                boat_payouts = re.findall(r"(\d+)\s+(\d+)", line)
                if boat_payouts:
                    betting_results["複勝1着"] = {
                        "艇番": boat_payouts[0][0],
                        "払戻金": boat_payouts[0][1],
                    }
                    if len(boat_payouts) > 1:
                        betting_results["複勝2着"] = {
                            "艇番": boat_payouts[1][0],
                            "払戻金": boat_payouts[1][1],
                        }

            elif "２連単" in line:
                # ２連単   1-3        390  人気     1
                match = re.search(r"２連単\s+(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                if match:
                    betting_results["2連単"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            elif "２連複" in line:
                # ２連複   1-3        310  人気     1
                match = re.search(r"２連複\s+(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                if match:
                    betting_results["2連複"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            elif "拡連複" in line:
                # 拡連複   1-3        190  人気     1
                match = re.search(r"拡連複\s+(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                if match:
                    if "拡連複1" not in betting_results:
                        betting_results["拡連複1"] = {
                            "艇番": match.group(1),
                            "払戻金": match.group(2),
                            "人気": match.group(3),
                        }
                    elif "拡連複2" not in betting_results:
                        betting_results["拡連複2"] = {
                            "艇番": match.group(1),
                            "払戻金": match.group(2),
                            "人気": match.group(3),
                        }
                    elif "拡連複3" not in betting_results:
                        betting_results["拡連複3"] = {
                            "艇番": match.group(1),
                            "払戻金": match.group(2),
                            "人気": match.group(3),
                        }

            elif (
                line.strip()
                and not line.startswith("単勝")
                and not line.startswith("複勝")
                and not line.startswith("２連")
                and not line.startswith("拡連複")
                and not line.startswith("３連")
            ):
                # 拡連複の続き行の処理
                match = re.search(r"(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                if match:
                    if "拡連複2" not in betting_results:
                        betting_results["拡連複2"] = {
                            "艇番": match.group(1),
                            "払戻金": match.group(2),
                            "人気": match.group(3),
                        }
                    elif "拡連複3" not in betting_results:
                        betting_results["拡連複3"] = {
                            "艇番": match.group(1),
                            "払戻金": match.group(2),
                            "人気": match.group(3),
                        }

            elif "３連単" in line:
                # ３連単   1-3-6     1830  人気     5
                match = re.search(
                    r"３連単\s+(\d+-\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line
                )
                if match:
                    betting_results["3連単"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            elif "３連複" in line:
                # ３連複   1-3-6      760  人気     3
                match = re.search(
                    r"３連複\s+(\d+-\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line
                )
                if match:
                    betting_results["3連複"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            i += 1

        return betting_results

    def parse_race_condition(self, line: str) -> Dict[str, str]:
        """レース条件を解析（距離、天候、風向、風速、波高）"""
        result = {
            "distance": "",
            "weather": "",
            "wind_direction": "",
            "wind_speed": "",
            "wave_height": "",
        }

        # 距離を抽出 (H1800m形式)
        distance_match = re.search(r"[HＨ](\d+)[mｍ]", line)
        if distance_match:
            result["distance"] = distance_match.group(1)

        # 天候を抽出 (晴、曇、雨など)
        weather_match = re.search(r"(晴|曇|雨|雪)　", line)
        if weather_match:
            result["weather"] = weather_match.group(1)

        # 風向と風速を抽出 (風  北　　 3m)
        wind_match = re.search(r"風\s+([^　\s]+)[\s　]+(\d+)m", line)
        if wind_match:
            result["wind_direction"] = wind_match.group(1)
            result["wind_speed"] = wind_match.group(2)

        # 波高を抽出 (波　  2cm)
        wave_match = re.search(r"波[\s　]+(\d+)cm", line)
        if wave_match:
            result["wave_height"] = wave_match.group(1)

        return result

    def parse_betting_results(
        self, lines: List[str], start_idx: int
    ) -> Dict[str, Dict]:
        """賭け式の払戻結果を解析"""
        betting_results = {}

        i = start_idx
        while i < len(lines):
            line = lines[i]  # strip()を削除

            # 次のレースの開始で終了
            if re.match(r"\s*\d+R\s+", line):
                break

            # 各賭け式の解析
            if "単勝" in line:
                match = re.search(r"単勝\s+(\d+)\s+(\d+)", line)
                if match:
                    betting_results["単勝"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                    }

            elif "複勝" in line:
                # 複勝は1着と2着がある場合がある
                matches = re.findall(r"(\d+)\s+(\d+)", line)
                if matches:
                    betting_results["複勝1着"] = {
                        "艇番": matches[0][0],
                        "払戻金": matches[0][1],
                    }
                    if len(matches) > 1:
                        betting_results["複勝2着"] = {
                            "艇番": matches[1][0],
                            "払戻金": matches[1][1],
                        }

            elif "２連単" in line:
                match = re.search(r"２連単\s+(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                if match:
                    betting_results["2連単"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            elif "２連複" in line:
                match = re.search(r"２連複\s+(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                if match:
                    betting_results["2連複"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            elif "拡連複" in line:
                # 拡連複は最大3つある
                if "拡連複1" not in betting_results:
                    match = re.search(
                        r"拡連複\s+(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line
                    )
                    if match:
                        betting_results["拡連複1"] = {
                            "艇番": match.group(1),
                            "払戻金": match.group(2),
                            "人気": match.group(3),
                        }
                else:
                    # 2番目以降の拡連複を解析
                    match = re.search(r"(\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line)
                    if match:
                        if "拡連複2" not in betting_results:
                            betting_results["拡連複2"] = {
                                "艇番": match.group(1),
                                "払戻金": match.group(2),
                                "人気": match.group(3),
                            }
                        elif "拡連複3" not in betting_results:
                            betting_results["拡連複3"] = {
                                "艇番": match.group(1),
                                "払戻金": match.group(2),
                                "人気": match.group(3),
                            }

            elif "３連単" in line:
                match = re.search(
                    r"３連単\s+(\d+-\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line
                )
                if match:
                    betting_results["3連単"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            elif "３連複" in line:
                match = re.search(
                    r"３連複\s+(\d+-\d+-\d+)\s+(\d+)\s+人気\s+(\d+)", line
                )
                if match:
                    betting_results["3連複"] = {
                        "艇番": match.group(1),
                        "払戻金": match.group(2),
                        "人気": match.group(3),
                    }

            i += 1

        return betting_results

    def parse_race_result(self, line: str) -> Optional[Dict]:
        """着順と競走結果を解析"""
        # 着順行のパターン: "  01  1 3501 川　上　　昇　平 50   12  6.89   1    0.08     1.49.7"
        # フィールド: 着順 艇番 登番 選手名 モーター ボート 展示 進入 スタート レースタイム

        if len(line) < 40:  # 最小限の長さチェック（緩和）
            return None

        # 区切り線をスキップ
        if line.strip().startswith("-"):
            return None

        # ヘッダー行をスキップ
        if "着" in line and "艇" in line and "登番" in line:
            return None

        # 着順データの先頭パターンチェック（2桁の空白 + 2桁の数字）
        if not line.startswith("  ") or len(line) < 4:
            return None

        try:
            # 着順（位置2-4の2桁）
            finish_pos = line[2:4].strip()

            # 着順の妥当性チェック（数字または失格コード）
            valid_finish_codes = [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "F",
                "S0",
                "S1",
                "S2",
                "L0",
                "L1",
                "K0",
                "K1",
            ]
            if finish_pos not in valid_finish_codes:
                return None

            # 艇番の位置を失格コードに応じて調整
            if finish_pos == "F":
                # フライングの場合: "  F   4 5155..." - 艇番は位置6
                boat_number = line[6:7].strip()
            elif finish_pos in ["S0", "S1", "S2"]:
                # スタート事故の場合: "  S1  1 4287..." - 艇番は位置6
                boat_number = line[6:7].strip()
            else:
                # 通常の着順の場合: "  01  1 3501..." - 艇番は位置6
                boat_number = line[6:7].strip()

            if not boat_number.isdigit():
                return None

            # 選手登番（位置8-11の4桁）
            player_id = line[8:12].strip()
            if not (player_id.isdigit() and len(player_id) == 4):
                return None

            # モーター番号（位置を調整）
            motor_number = ""
            if len(line) > 22:
                motor_number = line[22:24].strip()

            # ボート番号（位置を調整）
            boat_number_actual = ""
            if len(line) > 27:
                boat_number_actual = line[27:29].strip()

            # 展示タイム（位置を調整）
            exhibition_time = ""
            if len(line) > 31:
                exhibition_time = line[31:35].strip()

            # 進入コース（位置を調整）
            approach_course = ""
            if len(line) > 38:
                approach_course = line[38:39].strip()

            # スタートタイミング（位置を調整）
            start_timing = ""
            if len(line) > 42:
                # フライングの場合は位置42から、通常の場合は位置43からスタートタイミングを取得
                if finish_pos == "F":
                    start_timing = line[42:48].strip()
                else:
                    start_timing = line[43:49].strip()

                # フライングの場合は F0.08 -> -0.08 に変換
                if start_timing.startswith("F"):
                    start_timing = "-" + start_timing[1:]

            # レースタイム（位置を調整）
            race_time = ""
            if len(line) > 52:
                # フライングの場合は位置53から、通常の場合は位置52からレースタイムを取得
                if finish_pos == "F":
                    race_time = line[53:58].strip()
                else:
                    race_time = line[52:58].strip()

                # ".  ."の場合は空文字にする
                if race_time == ".  .":
                    race_time = ""

            return {
                "finish_position": finish_pos,
                "boat_number": boat_number,
                "player_id": player_id,
                "motor_number": motor_number,
                "boat_number_actual": boat_number_actual,
                "exhibition_time": exhibition_time,
                "approach_course": approach_course,
                "start_timing": start_timing,
                "race_time": race_time,
            }

        except (IndexError, ValueError):
            return None

    def process_race_section(self, lines: List[str], start_idx: int) -> Optional[Dict]:
        """レース区間を処理"""
        race_data = None
        race_results = {}
        betting_results = {}

        i = start_idx
        while i < len(lines):
            line = lines[i]  # strip()を削除して先頭の空白を保持

            # 次のレースの開始
            if re.search(r"^\s*\d+R\s+", line) and i > start_idx:
                break

            # レースヘッダーの解析（レース番号、距離、天候等）
            if re.search(r"^\s*\d+R\s+", line) and "H" in line:
                # レース番号を抽出
                race_match = re.search(r"(\d+)R", line)
                if race_match:
                    race_number = race_match.group(1)

                    # レース条件を解析
                    conditions = self.parse_race_condition(line)

                    race_data = {
                        "race_number": race_number,
                        "distance": conditions["distance"],
                        "weather": conditions["weather"],
                        "wind_direction": conditions["wind_direction"],
                        "wind_speed": conditions["wind_speed"],
                        "wave_height": conditions["wave_height"],
                    }

            # 着順結果の解析
            result_data = self.parse_race_result(line)
            if result_data:
                # 着順または失格コードをキーとして使用（重複を避けるため艇番も含める）
                key = result_data["finish_position"]
                if key in ["F", "S0", "S1", "S2", "L0", "L1", "K0", "K1"]:
                    # 失格の場合は艇番も含めてユニークなキーにする
                    key = f"{key}_{result_data['boat_number']}"
                race_results[key] = result_data

            # 払戻金情報の解析（単勝から始まる部分）
            if "単勝" in line and not betting_results:
                betting_results = self.parse_betting_results_in_race(lines, i)

            i += 1

        if race_data and race_results:
            race_data["race_results"] = race_results
            race_data["betting_results"] = betting_results
            return race_data

        return None

    def convert_file(self, year: int, month: int, day: int) -> int:
        """競走結果ファイルを変換"""
        # ファイル名生成
        year_short = year % 100
        input_file = f"data/raw/results/k{year_short:02d}{month:02d}{day:02d}_u8.txt"
        output_file = "data/race_results.csv"

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
            in_track_section = False

            i = 0
            while i < len(lines):
                line = lines[i]  # 元の行を保持
                line_stripped = line.strip()  # 比較用にstrip版も用意

                # トラック開始マーカー
                if re.match(r"\d{2}KBGN", line_stripped):
                    track_num = line_stripped[:2]
                    current_track_number = track_num
                    in_track_section = True
                    i += 1
                    continue

                # レース場名からトラック番号を抽出
                if (
                    not in_track_section
                    and current_track_number is None
                    and ("ボートレース" in line_stripped or "大　村" in line_stripped)
                ):
                    extracted_track = self.extract_track_number(line_stripped)
                    if extracted_track:
                        current_track_number = extracted_track
                        in_track_section = True
                    elif "大　村" in line_stripped:
                        current_track_number = "24"  # 大村は24番
                        in_track_section = True

                # トラック終了マーカー
                if re.match(r"\d{2}KEND", line_stripped):
                    current_track_number = None
                    in_track_section = False
                    i += 1
                    continue

                # レースヘッダーの検出 (例: "   1R       予選..." または "1R       予選...")
                if re.search(r"^\s*\d+R\s+", line) and "H" in line:
                    if in_track_section and current_track_number:
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
                        race["weather"],
                        race["wind_direction"],
                        race["wind_speed"],
                        race["wave_height"],
                    ]

                    # 賭け式結果を追加
                    betting = race["betting_results"]

                    # 単勝
                    single_win = betting.get("単勝", {})
                    row.extend(
                        [single_win.get("艇番", ""), single_win.get("払戻金", "")]
                    )

                    # 複勝
                    place1 = betting.get("複勝1着", {})
                    place2 = betting.get("複勝2着", {})
                    row.extend(
                        [
                            place1.get("艇番", ""),
                            place1.get("払戻金", ""),
                            place2.get("艇番", ""),
                            place2.get("払戻金", ""),
                        ]
                    )

                    # 2連単
                    exacta = betting.get("2連単", {})
                    row.extend(
                        [
                            exacta.get("艇番", ""),
                            exacta.get("払戻金", ""),
                            exacta.get("人気", ""),
                        ]
                    )

                    # 2連複
                    quinella = betting.get("2連複", {})
                    row.extend(
                        [
                            quinella.get("艇番", ""),
                            quinella.get("払戻金", ""),
                            quinella.get("人気", ""),
                        ]
                    )

                    # 拡連複
                    wide1 = betting.get("拡連複1", {})
                    wide2 = betting.get("拡連複2", {})
                    wide3 = betting.get("拡連複3", {})
                    row.extend(
                        [
                            wide1.get("艇番", ""),
                            wide1.get("払戻金", ""),
                            wide1.get("人気", ""),
                            wide2.get("艇番", ""),
                            wide2.get("払戻金", ""),
                            wide2.get("人気", ""),
                            wide3.get("艇番", ""),
                            wide3.get("払戻金", ""),
                            wide3.get("人気", ""),
                        ]
                    )

                    # 3連単
                    trifecta = betting.get("3連単", {})
                    row.extend(
                        [
                            trifecta.get("艇番", ""),
                            trifecta.get("払戻金", ""),
                            trifecta.get("人気", ""),
                        ]
                    )

                    # 3連複
                    trio = betting.get("3連複", {})
                    row.extend(
                        [
                            trio.get("艇番", ""),
                            trio.get("払戻金", ""),
                            trio.get("人気", ""),
                        ]
                    )

                    # 6艇分のレース結果を追加（艇番順）
                    finish_order = ["01", "02", "03", "04", "05", "06"]

                    # 全ての結果を収集
                    all_race_results = []

                    # 着順者を収集
                    for finish_pos in finish_order:
                        if finish_pos in race["race_results"]:
                            result = race["race_results"][finish_pos]
                            all_race_results.append(result)

                    # 失格者を収集（キーに艇番が含まれている）
                    for key, result in race["race_results"].items():
                        if "_" in key:  # 失格者のキー（例: "F_4", "S1_5"）
                            all_race_results.append(result)

                    # 艇番順でソート
                    all_race_results.sort(key=lambda x: int(x.get("boat_number", "0")))

                    # 6艇まで分の結果を出力（不足分は空で埋める）
                    for i in range(6):
                        if i < len(all_race_results):
                            result = all_race_results[i]
                        else:
                            result = {}

                        # 着順の先頭0を除去（01→1, 02→2, ...）
                        finish_pos = result.get("finish_position", "")
                        if (
                            finish_pos
                            and finish_pos.isdigit()
                            and finish_pos.startswith("0")
                        ):
                            finish_pos = finish_pos[1:]

                        row.extend(
                            [
                                finish_pos,
                                result.get("player_id", ""),
                                result.get("boat_number", ""),
                                result.get("motor_number", ""),
                                result.get("boat_number_actual", ""),
                                result.get("exhibition_time", ""),
                                result.get("approach_course", ""),
                                result.get("start_timing", ""),
                                result.get("race_time", ""),
                            ]
                        )

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
        print("使用方法: python convert_result.py YYYY MM DD")
        print("  YYYY: 年4桁（例: 2025）")
        print("  MM: 1桁または2桁の月（例: 7）")
        print("  DD: 1桁または2桁の日（例: 9）")
        return 1

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
    except ValueError:
        print("エラー: 引数は数値で入力してください")
        return 1

    try:
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
        converter = ResultConverter()
        return converter.convert_file(year, month, day)

    except Exception as e:
        print(f"エラー: 予期しないエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
