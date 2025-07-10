#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ボートレース結果データ変換プログラム
入力: k{年}{月:02d}{日:02d}_u8.txt
出力: race_results.csv
"""

import csv
import os
import re
import sys


def get_track_number(content):
    """競艇場番号を取得する"""
    track_map = {
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

    # ファイル先頭の24KBGNから取得（最も確実）
    match = re.search(r"^(\d{2})KBGN", content, re.MULTILINE)
    if match:
        return match.group(1)

    # ファイル内から競艇場名を検索（全角スペースを含む可能性を考慮）
    track_match = re.search(r"ボートレース([^\n\r]+)", content)
    if track_match:
        track_name_raw = track_match.group(1).strip()
        # 全角スペースを除去して競艇場名を抽出
        track_name = re.sub(r"[　\s]+", "", track_name_raw)
        return track_map.get(track_name, "00")

    return "00"


def parse_race_header(race_content):
    """レースヘッダーから基本情報を抽出"""
    # 距離、天候、風向き、風速、波高を抽出
    # 例: H1800m  雨　  風  北東　 5m  波　  4cm
    header_pattern = r"H(\d+)m\s+([^\s]+)\s+風\s+([^\s]+)\s+(\d+)m\s+波\s+(\d+)cm"
    match = re.search(header_pattern, race_content)

    if match:
        return {
            "distance": match.group(1),
            "weather": match.group(2),
            "wind_direction": match.group(3),
            "wind_speed": match.group(4),
            "wave_height": match.group(5),
        }
    return {}


def parse_boat_result(line):
    """1行の艇結果を解析"""
    # 着順、艇番、登番、選手名、モーター、ボート、展示タイム、進入、スタートタイミング、レースタイム
    # 例: 01  5 3784 中　島　　友　和 40   75  6.89   5    0.10     1.51.0
    # 特殊着順例: S0  5 3784 中　島　　友　和 40   75  6.89   5    F0.10     1.51.0

    # 着順は数字(01-06)または特殊コード(S0,S1,S2,F,L0,L1,K0,K1)
    # スタートタイミングはFで始まる場合もある
    pattern = r"\s*([0-9]{1,2}|S[0-2]|F|L[01]|K[01])\s+(\d)\s+(\d+)\s+([^\d]+?)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d)\s+(F?[\d.-]+)\s+([\d:.]+|\.+)"
    match = re.match(pattern, line)

    if match:
        # スタートタイミングの処理（Fが付いている場合は-に変換）
        start_timing = match.group(9).strip()
        if start_timing.startswith("F"):
            start_timing = "-" + start_timing[1:]  # F0.10 → -0.10

        return {
            "position": match.group(1).strip(),
            "boat_number": match.group(2).strip(),
            "registration_number": match.group(3).strip(),
            "motor": match.group(5).strip(),
            "boat": match.group(6).strip(),
            "exhibition_time": match.group(7).strip(),
            "entry_number": match.group(8).strip(),
            "start_timing": start_timing,
            "race_time": (
                match.group(10).strip()
                if match.group(10) != "." and "." in match.group(10)
                else ""
            ),
        }
    return None


def parse_race_data(file_path, year, month, day):
    """レース結果ファイルを解析してCSVデータを作成"""
    results = []

    try:
        # UTF-8で試す
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        # Shift_JISで試す
        with open(file_path, "r", encoding="shift_jis") as f:
            content = f.read()

    # 競艇場ごとのセクションを分割（[番号]KBGN から [番号]KEND まで）
    track_pattern = r"(\d{2})KBGN(.*?)(\d{2})KEND"
    tracks = re.findall(track_pattern, content, re.DOTALL)

    for track_start_num, track_content, track_end_num in tracks:
        # 開始番号と終了番号が一致することを確認
        if track_start_num == track_end_num:
            track_number = track_start_num
            results.extend(
                process_track_section(track_content, track_number, year, month, day)
            )

    return results


def process_track_section(track_content, track_number, year, month, day):
    """1つの競艇場のセクションを処理"""
    results = []

    # レースごとに分割 (1R, 2R, ... で分割)
    race_pattern = r"\n\s*(\d{1,2})R\s+([^\n]*)\n(.*?)(?=\n\s*\d{1,2}R\s+|\n\s*第|\Z)"
    races = re.findall(race_pattern, track_content, re.DOTALL)

    for race_number, race_header, race_content in races:
        # レース基本情報を取得（ヘッダー行から）
        race_info = parse_race_header(race_header + "\n" + race_content)

        # 着順データの部分を抽出
        lines = race_content.split("\n")
        in_results = False

        for line in lines:
            if "着 艇 登番" in line:
                in_results = True
                continue
            if in_results and ("---" in line):
                continue
            if in_results and (line.strip() == "" or "単勝" in line or "複勝" in line):
                break

            if in_results and line.strip():
                boat_result = parse_boat_result(line)
                if boat_result:
                    # CSVの1行を作成
                    row = [
                        year,
                        month,
                        day,
                        track_number,
                        race_number,
                        race_info.get("distance", ""),
                        race_info.get("weather", ""),
                        race_info.get("wind_direction", ""),
                        race_info.get("wind_speed", ""),
                        race_info.get("wave_height", ""),
                        boat_result["position"],
                        boat_result["boat_number"],
                        boat_result["registration_number"],
                        boat_result["motor"],
                        boat_result["boat"],
                        boat_result["exhibition_time"],
                        boat_result["entry_number"],
                        boat_result["start_timing"],
                        boat_result["race_time"],
                    ]
                    results.append(row)

    return results


def write_csv(results, output_file):
    """結果をCSVファイルに出力"""
    headers = [
        "年",
        "月",
        "日",
        "競艇場番号",
        "レース番号",
        "距離",
        "天候",
        "風向き",
        "風速",
        "波高",
        "着",
        "艇",
        "登番",
        "モーター",
        "ボート",
        "展示タイム",
        "進入番号",
        "スタートタイミング",
        "レースタイム",
    ]

    # ファイルが存在するかチェック
    file_exists = os.path.exists(output_file)

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ヘッダーを書き込み（ファイルが新規の場合のみ）
        if not file_exists:
            writer.writerow(headers)

        # データを書き込み
        for row in results:
            writer.writerow(row)


def main():
    """メイン関数"""
    if len(sys.argv) != 4:
        print("使用方法: python convert_race_result.py <年> <月> <日>")
        print("例: python convert_race_result.py 2025 7 9")
        sys.exit(1)

    try:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
    except ValueError:
        print("エラー: 年、月、日は数値で入力してください")
        sys.exit(1)

    # 入力ファイル名を生成
    input_filename = f"k{year % 100:02d}{month:02d}{day:02d}_u8.txt"
    input_path = os.path.join("data", "raw", "results", input_filename)

    # ファイルの存在確認
    if not os.path.exists(input_path):
        print(f"エラー: ファイル {input_path} が見つかりません")
        sys.exit(1)

    print(f"処理開始: {input_path}")

    # データを解析
    results = parse_race_data(input_path, year, month, day)

    if not results:
        print("エラー: データが見つかりませんでした")
        sys.exit(1)

    # CSVファイルに出力
    output_file = "race_results.csv"
    write_csv(results, output_file)

    print(f"変換完了: {len(results)}件のデータを {output_file} に出力しました")


if __name__ == "__main__":
    main()
