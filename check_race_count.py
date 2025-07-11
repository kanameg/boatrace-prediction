#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
レース数チェックプログラム

各日付の各レース場で12レースが存在するかチェックする
"""

import csv
import sys
from collections import defaultdict
from typing import Dict, List, Tuple


def check_race_count(csv_file: str, show_all: bool = False) -> None:
    """CSVファイル内のレース数をチェック"""
    # データ構造: {(年, 月, 日, レース場番号): [レース番号のリスト]}
    race_data = defaultdict(list)

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                year = int(row["年"])
                month = int(row["月"])
                day = int(row["日"])
                track_num = row["レース場番号"]
                race_num = int(row["レース番号"])

                key = (year, month, day, track_num)
                race_data[key].append(race_num)

    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません: {csv_file}")
        return
    except Exception as e:
        print(f"エラー: ファイル読み込み中にエラーが発生しました: {e}")
        return

    # レース場番号の名前マッピング
    track_names = {
        "01": "桐生",
        "02": "戸田",
        "03": "江戸川",
        "04": "平和島",
        "05": "多摩川",
        "06": "浜名湖",
        "07": "蒲郡",
        "08": "常滑",
        "09": "津",
        "10": "三国",
        "11": "びわこ",
        "12": "住之江",
        "13": "尼崎",
        "14": "鳴門",
        "15": "丸亀",
        "16": "児島",
        "17": "宮島",
        "18": "徳山",
        "19": "下関",
        "20": "若松",
        "21": "芦屋",
        "22": "福岡",
        "23": "唐津",
        "24": "大村",
    }

    # 分析結果
    total_entries = len(race_data)
    incomplete_tracks = []
    complete_tracks = []
    missing_races = []

    print("=== レース数チェック結果 ===\n")

    # 各トラック・日付の組み合わせをチェック
    for key, races in sorted(race_data.items()):
        year, month, day, track_num = key
        track_name = track_names.get(track_num, f"不明({track_num})")

        race_count = len(races)
        races_sorted = sorted(races)
        expected_races = list(range(1, 13))  # 1-12レース

        date_str = f"{year}年{month:02d}月{day:02d}日"
        track_info = f"{track_name}({track_num})"

        if race_count == 12 and races_sorted == expected_races:
            complete_tracks.append((date_str, track_info))
        else:
            incomplete_tracks.append((date_str, track_info, race_count, races_sorted))

            # 欠けているレースを特定
            missing = [r for r in expected_races if r not in races]
            extra = [r for r in races if r not in expected_races]

            missing_races.append(
                {
                    "date": date_str,
                    "track": track_info,
                    "count": race_count,
                    "races": races_sorted,
                    "missing": missing,
                    "extra": extra,
                }
            )

    # 結果表示
    print(f"総チェック対象: {total_entries} トラック・日付")
    print(f"完全なデータ: {len(complete_tracks)} トラック・日付")
    print(f"不完全なデータ: {len(incomplete_tracks)} トラック・日付")
    print()

    # 全てのデータを日付・レース場ごとに表示
    if show_all:
        print("=== 日付・レース場別レース数一覧（全て） ===")
        current_date = ""
        for key, races in sorted(race_data.items()):
            year, month, day, track_num = key
            track_name = track_names.get(track_num, f"不明({track_num})")

            race_count = len(races)
            races_sorted = sorted(races)
            expected_races = list(range(1, 13))  # 1-12レース

            date_str = f"{year}年{month:02d}月{day:02d}日"

            # 日付が変わったら改行
            if current_date != date_str:
                if current_date != "":
                    print()
                print(f"【{date_str}】")
                current_date = date_str

            # レース数の状態表示
            status = "✓" if race_count == 12 and races_sorted == expected_races else "✗"
            print(f"  {track_name}({track_num}): {race_count}レース {status}")

            # 不完全なデータの場合は詳細表示
            if race_count != 12 or races_sorted != expected_races:
                print(f"    実際のレース: {races_sorted}")
                missing = [r for r in expected_races if r not in races]
                extra = [r for r in races if r not in expected_races]

                if missing:
                    print(f"    欠けているレース: {missing}")
                if extra:
                    print(f"    余分なレース: {extra}")
    else:
        print("=== 不完全なデータのみ（日付・レース場別） ===")
        current_date = ""
        for key, races in sorted(race_data.items()):
            year, month, day, track_num = key
            track_name = track_names.get(track_num, f"不明({track_num})")

            race_count = len(races)
            races_sorted = sorted(races)
            expected_races = list(range(1, 13))  # 1-12レース

            # 不完全なデータのみ表示
            if race_count != 12 or races_sorted != expected_races:
                date_str = f"{year}年{month:02d}月{day:02d}日"

                # 日付が変わったら改行（不完全データがある場合のみ）
                if current_date != date_str:
                    if current_date != "":
                        print()
                    print(f"【{date_str}】")
                    current_date = date_str

                print(f"  {track_name}({track_num}): {race_count}レース ✗")
                print(f"    実際のレース: {races_sorted}")

                missing = [r for r in expected_races if r not in races]
                extra = [r for r in races if r not in expected_races]

                if missing:
                    print(f"    欠けているレース: {missing}")
                if extra:
                    print(f"    余分なレース: {extra}")

    print()

    if incomplete_tracks:
        print("=== 不完全なデータのサマリー ===")
        for entry in missing_races:
            print(
                f"{entry['date']} {entry['track']}: {entry['count']}レース (欠け: {entry['missing']}, 余分: {entry['extra']})"
            )
        print()

    # 統計情報
    print("=== 統計情報 ===")

    # 日付別の集計
    date_stats = defaultdict(lambda: {"total": 0, "complete": 0})
    track_stats = defaultdict(lambda: {"total": 0, "complete": 0})

    for key, races in race_data.items():
        year, month, day, track_num = key
        date_key = f"{year}-{month:02d}-{day:02d}"
        track_name = track_names.get(track_num, f"不明({track_num})")

        is_complete = len(races) == 12 and sorted(races) == list(range(1, 13))

        date_stats[date_key]["total"] += 1
        track_stats[track_name]["total"] += 1

        if is_complete:
            date_stats[date_key]["complete"] += 1
            track_stats[track_name]["complete"] += 1

    # 日付別統計の表示
    print("\n日付別完了率:")
    for date, stats in sorted(date_stats.items()):
        rate = (stats["complete"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"  {date}: {stats['complete']}/{stats['total']} トラック ({rate:.1f}%)")

    # トラック別統計の表示
    print("\nトラック別完了率:")
    for track, stats in sorted(track_stats.items()):
        rate = (stats["complete"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        print(f"  {track}: {stats['complete']}/{stats['total']} 日 ({rate:.1f}%)")

    # 全体の完了率
    overall_rate = (
        (len(complete_tracks) / total_entries) * 100 if total_entries > 0 else 0
    )
    print(f"\n全体完了率: {len(complete_tracks)}/{total_entries} ({overall_rate:.1f}%)")


def main():
    """メイン関数"""
    csv_file = "data/race_programs.csv"
    show_all = False

    # コマンドライン引数の解析
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--all":
                show_all = True
            elif not arg.startswith("--"):
                csv_file = arg

    if "--help" in sys.argv or "-h" in sys.argv:
        print("使用方法: python check_race_count.py [ファイル名] [--all]")
        print(
            "  ファイル名: チェックするCSVファイル（デフォルト: data/race_programs.csv）"
        )
        print("  --all: 全てのデータを表示（デフォルト: 不完全なデータのみ表示）")
        return

    check_race_count(csv_file, show_all)


if __name__ == "__main__":
    main()
