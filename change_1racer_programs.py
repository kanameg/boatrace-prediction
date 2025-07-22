#!/usr/bin/env python3
"""
レース番組表データを各枠ごとに1行に変換し、着順情報を追加するプログラム
"""

import pandas as pd


def load_race_results():
    """レース結果データを読み込み、着順情報の辞書を作成"""
    print("results.csvを読み込み中...")
    results_df = pd.read_csv("/app/data/results.csv")

    # 着順情報を辞書で管理（キー: (年, 月, 日, レース場番号, レース番号, 選手登番), 値: 着順）
    ranking_dict = {}

    for _, row in results_df.iterrows():
        # 各艇の着順情報を抽出
        for frame in range(1, 7):
            key = (
                row["年"],
                row["月"],
                row["日"],
                row["レース場番号"],
                row["レース番号"],
                row[f"{frame}艇_選手登番"],
            )
            ranking_dict[key] = row[f"{frame}艇_着順"]

    print(f"着順情報を{len(ranking_dict)}件読み込みました")
    return ranking_dict


def load_racer_data():
    """選手データを読み込み、コース別複勝率、平均スタート順位、1着回数、2着回数の辞書を作成"""
    print("racers.csvを読み込み中...")
    racer_df = pd.read_csv("/app/data/racers.csv")

    # 選手登番をキーとして、各コース複勝率、平均スタート順位、1着回数、2着回数を辞書で管理
    racer_dict = {}
    for _, row in racer_df.iterrows():
        racer_dict[row["登番"]] = {
            "1コース複勝率": row.get("1コース複勝率", ""),
            "2コース複勝率": row.get("2コース複勝率", ""),
            "3コース複勝率": row.get("3コース複勝率", ""),
            "4コース複勝率": row.get("4コース複勝率", ""),
            "5コース複勝率": row.get("5コース複勝率", ""),
            "6コース複勝率": row.get("6コース複勝率", ""),
            "1コース平均スタート順位": row.get("1コース平均スタート順位", ""),
            "2コース平均スタート順位": row.get("2コース平均スタート順位", ""),
            "3コース平均スタート順位": row.get("3コース平均スタート順位", ""),
            "4コース平均スタート順位": row.get("4コース平均スタート順位", ""),
            "5コース平均スタート順位": row.get("5コース平均スタート順位", ""),
            "6コース平均スタート順位": row.get("6コース平均スタート順位", ""),
            "1コース1着回数": row.get("1コース1着回数", ""),
            "2コース1着回数": row.get("2コース1着回数", ""),
            "3コース1着回数": row.get("3コース1着回数", ""),
            "4コース1着回数": row.get("4コース1着回数", ""),
            "5コース1着回数": row.get("5コース1着回数", ""),
            "6コース1着回数": row.get("6コース1着回数", ""),
            "1コース2着回数": row.get("1コース2着回数", ""),
            "2コース2着回数": row.get("2コース2着回数", ""),
            "3コース2着回数": row.get("3コース2着回数", ""),
            "4コース2着回数": row.get("4コース2着回数", ""),
            "5コース2着回数": row.get("5コース2着回数", ""),
            "6コース2着回数": row.get("6コース2着回数", ""),
            "1着回数": row.get("1着回数", ""),
            "2着回数": row.get("2着回数", ""),
        }

    print(f"選手データを{len(racer_dict)}件読み込みました")
    return racer_dict


def convert_race_programs():
    """programs.csvを読み込み、各枠ごとに1行に変換し、着順情報とコース別複勝率を追加してracer_program.csvに保存"""

    # 着順情報を読み込み
    ranking_dict = load_race_results()

    # 選手データを読み込み
    racer_dict = load_racer_data()

    # データを読み込み
    print("programs.csvを読み込み中...")
    df = pd.read_csv("/app/data/programs.csv")

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
            "距離": row["距離"],
            "投票締切時間": row["投票締切時間"],
        }

        # 各枠（1艇から6艇）の情報を抽出
        for frame in range(1, 7):
            frame_data = common_data.copy()
            frame_data["枠番"] = frame

            # 各枠の詳細情報を追加
            prefix = f"{frame}艇_"
            racer_number = row.get(f"{prefix}選手登番", "")
            frame_data["選手登番"] = racer_number
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

            # コース別複勝率を追加（枠番に対応するコース複勝率）
            if racer_number and racer_number in racer_dict:
                course_key = f"{frame}コース複勝率"
                frame_data["コース別複勝率"] = racer_dict[racer_number].get(
                    course_key, ""
                )
            else:
                frame_data["コース別複勝率"] = ""

            # コース別平均スタート順位を追加（枠番に対応するコース平均スタート順位）
            if racer_number and racer_number in racer_dict:
                start_rank_key = f"{frame}コース平均スタート順位"
                frame_data["コース別平均スタート順位"] = racer_dict[racer_number].get(
                    start_rank_key, ""
                )
            else:
                frame_data["コース別平均スタート順位"] = ""

            # コース別1着回数を追加（枠番に対応するコース1着回数）
            if racer_number and racer_number in racer_dict:
                first_key = f"{frame}コース1着回数"
                frame_data["コース別1着回数"] = racer_dict[racer_number].get(
                    first_key, ""
                )
            else:
                frame_data["コース別1着回数"] = ""

            # コース別2着回数を追加（枠番に対応するコース2着回数）
            if racer_number and racer_number in racer_dict:
                second_key = f"{frame}コース2着回数"
                frame_data["コース別2着回数"] = racer_dict[racer_number].get(
                    second_key, ""
                )
            else:
                frame_data["コース別2着回数"] = ""

            # 全体1着回数を追加
            if racer_number and racer_number in racer_dict:
                frame_data["1着回数"] = racer_dict[racer_number].get("1着回数", "")
            else:
                frame_data["1着回数"] = ""

            # 全体2着回数を追加
            if racer_number and racer_number in racer_dict:
                frame_data["2着回数"] = racer_dict[racer_number].get("2着回数", "")
            else:
                frame_data["2着回数"] = ""

            # 着順情報を追加
            key = (
                row["年"],
                row["月"],
                row["日"],
                row["レース場番号"],
                row["レース番号"],
                racer_number,
            )
            ranking = ranking_dict.get(key, "")
            frame_data["着順"] = ranking

            # 勝敗情報を追加（着順が1なら1、それ以外は0）
            try:
                if ranking == 1 or ranking == "1" or int(ranking) == 1:
                    frame_data["勝敗"] = 1
                elif ranking == 2 or ranking == "2" or int(ranking) == 2:
                    frame_data["勝敗"] = 1
                else:
                    frame_data["勝敗"] = 0
            except (ValueError, TypeError):
                # 着順データがない場合や変換できない場合は空欄
                frame_data["勝敗"] = ""

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
        "距離",
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
        "コース別複勝率",
        "コース別平均スタート順位",
        "コース別1着回数",
        "コース別2着回数",
        "1着回数",
        "2着回数",
        "着順",
        "勝敗",
    ]

    result_df = result_df[columns_order]

    # ファイルに保存
    output_file = "/app/data/racer_program.csv"
    result_df.to_csv(output_file, index=False)

    print(
        f"変換完了: {len(df)}行のレースデータから{len(result_df)}行の選手データに変換（着順・勝敗情報付き）"
    )
    print(f"出力ファイル: {output_file}")

    # 変換結果の確認表示
    print("\n変換結果の先頭5行:")
    print(result_df.head())

    print("\n変換結果の末尾5行:")
    print(result_df.tail())

    return result_df


if __name__ == "__main__":
    convert_race_programs()
