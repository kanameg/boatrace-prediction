#!/usr/bin/env python3
"""
レース番組表データを各枠ごとに1行に変換するプログラム
"""

import sys

import pandas as pd


def convert_race_programs():
    """race_programs.csvを読み込み、各枠ごとに1行に変換してracer_program.csvに保存"""

    # データを読み込み
    print("race_programs.csvを読み込み中...")
    df = pd.read_csv("/app/data/race_programs.csv")

    # 変換後のデータを格納するリスト
    converted_rows = []

    # 各行を処理
    for _, row in df.iterrows():
        # 共通情報
        common_data = {
            "年": row["年"],
            "月": row["月"],
            "日": row["日"],
            "レース場番号": row["レース場番号"],
            "レース番号": row["レース番号"],
            "距離(m)": row["距離(m)"],
            "投票締切時間": row["投票締切時間"],
        }

        # 各枠（1艇から6艇）の情報を抽出
        for frame in range(1, 7):
            frame_data = common_data.copy()
            frame_data["枠番"] = frame

            # 各枠の詳細情報を追加
            prefix = f"{frame}艇_"
            frame_data["選手登番"] = row.get(f"{prefix}選手登番", "")
            frame_data["年齢"] = row.get(f"{prefix}年齢", "")
            frame_data["支部"] = row.get(f"{prefix}支部", "")
            frame_data["体重"] = row.get(f"{prefix}体重", "")
            frame_data["級別"] = row.get(f"{prefix}級別", "")
            frame_data["全国勝率"] = row.get(f"{prefix}全国勝率", "")
            frame_data["全国2連率"] = row.get(f"{prefix}全国2連率", "")
            frame_data["当地勝率"] = row.get(f"{prefix}当地勝率", "")
            frame_data["当地2連率"] = row.get(f"{prefix}当地2連率", "")
            frame_data["モーター番号"] = row.get(f"{prefix}モーター番号", "")
            frame_data["モーター2連率"] = row.get(f"{prefix}モーター2連率", "")
            frame_data["ボート番号"] = row.get(f"{prefix}ボート番号", "")
            frame_data["ボート2連率"] = row.get(f"{prefix}ボート2連率", "")

            converted_rows.append(frame_data)

    # DataFrameに変換
    result_df = pd.DataFrame(converted_rows)

    # カラムの順序を調整
    columns_order = [
        "年",
        "月",
        "日",
        "レース場番号",
        "レース番号",
        "距離(m)",
        "投票締切時間",
        "枠番",
        "選手登番",
        "年齢",
        "支部",
        "体重",
        "級別",
        "全国勝率",
        "全国2連率",
        "当地勝率",
        "当地2連率",
        "モーター番号",
        "モーター2連率",
        "ボート番号",
        "ボート2連率",
    ]

    result_df = result_df[columns_order]

    # ファイルに保存
    output_file = "/app/data/racer_program.csv"
    result_df.to_csv(output_file, index=False)

    print(
        f"変換完了: {len(df)}行のレースデータから{len(result_df)}行の選手データに変換"
    )
    print(f"出力ファイル: {output_file}")

    # 変換結果の確認表示
    print("\n変換結果の先頭5行:")
    print(result_df.head())

    return result_df


if __name__ == "__main__":
    convert_race_programs()
