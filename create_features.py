def make_feature_wakuban(programs_df):
    """
    枠番特徴量を作成
    """
    return programs_df["枠番"]


def make_feature_grade(programs_df):
    """
    級別特徴量を作成（数値変換）
    """
    return programs_df["級別"].apply(grade_to_numeric)


#!/usr/bin/env python3
"""
特徴量作成スクリプト

競艇予測のための特徴量を作成するスクリプトです。
trainモードでは学習用データを、predモードでは予測用データを作成します。

使用方法:
    python create_features.py train 2025-01-01 2025-07-18    # 学習用データ作成
    python create_features.py train 2025-01-01               # 学習用データ作成（終了日指定なし）
    python create_features.py train                          # 学習用データ作成（全期間）
    python create_features.py pred 2025-07-20                # 予測用データ作成
"""

import argparse
import sys
from datetime import datetime

import numpy as np
import pandas as pd


def make_race_id(row):
    """
    Create a unique race ID from date, place number, and race number.
    Args:
        row: DataFrame row
    Returns:
        int: Race ID (YYYYMMDDPPRRR as integer)
    """
    date_str = f"{row['年']:04d}{row['月']:02d}{row['日']:02d}"
    place_str = f"{row['レース場番号']:02d}"
    race_str = f"{row['レース番号']:02d}"
    return int(f"{date_str}{place_str}{race_str}")


def make_racer_id(row):
    """
    Create a unique racer ID from racer number, and course number.
    Args:
        row: DataFrame row
    Returns:
        int: Racer ID (NNNNNC as integer)
    """
    racer_id = f"{row['選手登番']:05d}"
    course = f"{row['枠番']:01d}"
    return int(f"{racer_id}{course}")


def grade_to_numeric(grade):
    """
    Convert grade to numeric value.
    Args:
        grade: Grade (A1, A2, B1, B2)
    Returns:
        int: Numeric grade (A1:3, A2:2, B1:1, B2:0)
    """
    if grade == "A1":
        return 3
    elif grade == "A2":
        return 2
    elif grade == "B1":
        return 1
    elif grade == "B2":
        return 0
    else:
        return np.nan


# ---------------------------------------------------
# 特徴量生成関数群
# ---------------------------------------------------
def make_feature_lane_win_rate(programs_df, racers_df):
    """
    コース別複勝率特徴量を作成
    """

    def get_lane_win_rate(row):
        column_map = {
            1: "1コース複勝率",
            2: "2コース複勝率",
            3: "3コース複勝率",
            4: "4コース複勝率",
            5: "5コース複勝率",
            6: "6コース複勝率",
        }
        racer_id = row["選手登番"]
        lane = row["枠番"]
        col_name = column_map.get(lane)
        if col_name is None:
            return np.nan
        matched_rows = racers_df[racers_df["登番"] == racer_id]
        if len(matched_rows) == 0:
            return np.nan
        return np.round(
            pd.to_numeric(matched_rows.iloc[-1][col_name], errors="coerce"), decimals=3
        )

    return programs_df.apply(get_lane_win_rate, axis=1)


def make_feature_lane_1st_place(programs_df, racers_df):
    """
    コース別1着率特徴量を作成
    """

    def get_lane_1st_place_rate(row):
        column_1st_place_map = {
            1: "1コース1着回数",
            2: "2コース1着回数",
            3: "3コース1着回数",
            4: "4コース1着回数",
            5: "5コース1着回数",
            6: "6コース1着回数",
        }
        column_cource_entries_map = {
            1: "1コース進入回数",
            2: "2コース進入回数",
            3: "3コース進入回数",
            4: "4コース進入回数",
            5: "5コース進入回数",
            6: "6コース進入回数",
        }
        racer_id = row["選手登番"]
        lane = row["枠番"]
        col_1st_place_name = column_1st_place_map.get(lane)
        if col_1st_place_name is None:
            return np.nan
        col_cource_entries_name = column_cource_entries_map.get(lane)
        if col_cource_entries_name is None:
            return np.nan
        matched_rows = racers_df[racers_df["登番"] == racer_id]
        if len(matched_rows) == 0:
            return np.nan
        num_1st_place = pd.to_numeric(
            matched_rows.iloc[-1][col_1st_place_name], errors="coerce"
        )
        num_cource_entries = pd.to_numeric(
            matched_rows.iloc[-1][col_cource_entries_name], errors="coerce"
        )
        rate_1st_place = np.round(
            num_1st_place / num_cource_entries if num_cource_entries > 0 else 0,
            decimals=3,
        )
        return rate_1st_place

    return programs_df.apply(get_lane_1st_place_rate, axis=1)


def make_feature_race_win_rate_diff(programs_df):
    """
    レース内全国勝率差特徴量を作成
    """

    def calc_rate_diff(rates):
        rates_numeric = pd.to_numeric(rates, errors="coerce")
        avg_rate = rates_numeric.mean()
        return np.round(rates_numeric - avg_rate, decimals=3)

    return programs_df.groupby("レースID")["全国勝率"].transform(calc_rate_diff)


def make_feature_race_lane_1st_place_diff(programs_df):
    """
    レース内コース別1着率差特徴量を作成
    """

    def calc_rate_diff(rates):
        rates_numeric = pd.to_numeric(rates, errors="coerce")
        avg_rate = rates_numeric.mean()
        return np.round(rates_numeric - avg_rate, decimals=3)

    return programs_df.groupby("レースID")["コース別1着率"].transform(calc_rate_diff)


def make_feature_race_lane_win_rate_diff(programs_df):
    """
    レース内コース別複勝率差特徴量を作成
    """

    def calc_rate_diff(rates):
        rates_numeric = pd.to_numeric(rates, errors="coerce")
        avg_rate = rates_numeric.mean()
        return np.round(rates_numeric - avg_rate, decimals=3)

    return programs_df.groupby("レースID")["コース別複勝率"].transform(calc_rate_diff)


def make_feature_first_place_flag(merged_df):
    """
    1着フラグ特徴量を作成
    """
    merged_df["着順"] = pd.to_numeric(merged_df["着順"], errors="coerce")
    return (merged_df["着順"] == 1).astype(int)


def load_and_preprocess_programs(file_path, start_date=None, end_date=None):
    """
    programs.csvを読み込み、前処理を行う

    Args:
        file_path: CSVファイルのパス
        start_date: 開始日 (YYYY-MM-DD形式)
        end_date: 終了日 (YYYY-MM-DD形式)

    Returns:
        pd.DataFrame: 前処理済みのデータフレーム
    """
    print("=== programs.csvを読み込み中 ===")
    programs_df = pd.read_csv(file_path)
    print(f"読み込み完了: {programs_df.shape}")

    # 日付フィルタリング
    if start_date or end_date:
        programs_df["開催日"] = pd.to_datetime(
            programs_df[["年", "月", "日"]].astype(str).agg("-".join, axis=1)
        )

        if start_date:
            start_date_dt = pd.to_datetime(start_date)
            programs_df = programs_df[programs_df["開催日"] >= start_date_dt]
            print(f"開始日フィルタ適用 ({start_date}): {programs_df.shape}")

        if end_date:
            end_date_dt = pd.to_datetime(end_date)
            programs_df = programs_df[programs_df["開催日"] <= end_date_dt]
            print(f"終了日フィルタ適用 ({end_date}): {programs_df.shape}")

        # データが0件の場合はエラー
        if len(programs_df) == 0:
            print(f"エラー: 指定された日付範囲にデータが存在しません")
            print(f"指定範囲: {start_date or '指定なし'} ～ {end_date or '指定なし'}")
            # データの実際の期間を表示
            original_df = pd.read_csv(file_path)
            original_df["開催日"] = pd.to_datetime(
                original_df[["年", "月", "日"]].astype(str).agg("-".join, axis=1)
            )
            print(
                f"利用可能な期間: {original_df['開催日'].min().date()} ～ {original_df['開催日'].max().date()}"
            )
            sys.exit(1)

    # 必要な基本カラムを抽出
    features_df = pd.DataFrame()
    features_df["レースID"] = programs_df.apply(make_race_id, axis=1)

    # ---------------------------------------------------
    # 番組情報からの特徴量
    # ---------------------------------------------------
    features_df["枠番"] = make_feature_wakuban(programs_df)
    features_df["級別"] = make_feature_grade(programs_df)

    # ---------------------------------------------------
    # 選手情報を必要とする特徴量
    # ---------------------------------------------------
    racers_df = pd.read_csv("data/racers.csv")

    features_df["コース別複勝率"] = make_feature_lane_win_rate(programs_df, racers_df)
    features_df["コース別1着率"] = make_feature_lane_1st_place(programs_df, racers_df)
    features_df["レース内全国勝率差"] = make_feature_race_win_rate_diff(programs_df)
    features_df["レース内コース別1着率差"] = make_feature_race_lane_1st_place_diff(
        programs_df
    )
    features_df["レース内コース別複勝率差"] = make_feature_race_lane_win_rate_diff(
        programs_df
    )
    print(f"前処理完了: {features_df.shape}")

    return features_df


def load_and_preprocess_results(file_path, start_date=None, end_date=None):
    """
    results.csvを読み込み、前処理を行う

    Args:
        file_path: CSVファイルのパス
        start_date: 開始日 (YYYY-MM-DD形式)
        end_date: 終了日 (YYYY-MM-DD形式)

    Returns:
        pd.DataFrame: 前処理済みのデータフレーム
    """
    print("=== results.csvを読み込み中 ===")
    results_df = pd.read_csv(file_path)
    print(f"読み込み完了: {results_df.shape}")

    # 日付フィルタリング
    if start_date or end_date:
        results_df["開催日"] = pd.to_datetime(
            results_df[["年", "月", "日"]].astype(str).agg("-".join, axis=1)
        )

        if start_date:
            start_date_dt = pd.to_datetime(start_date)
            results_df = results_df[results_df["開催日"] >= start_date_dt]
            print(f"開始日フィルタ適用 ({start_date}): {results_df.shape}")

        if end_date:
            end_date_dt = pd.to_datetime(end_date)
            results_df = results_df[results_df["開催日"] <= end_date_dt]
            print(f"終了日フィルタ適用 ({end_date}): {results_df.shape}")

        # データが0件の場合はエラー
        if len(results_df) == 0:
            print(f"エラー: 指定された日付範囲にresults.csvのデータが存在しません")
            print(f"指定範囲: {start_date or '指定なし'} ～ {end_date or '指定なし'}")
            # データの実際の期間を表示
            original_df = pd.read_csv(file_path)
            original_df["開催日"] = pd.to_datetime(
                original_df[["年", "月", "日"]].astype(str).agg("-".join, axis=1)
            )
            print(
                f"利用可能な期間: {original_df['開催日'].min().date()} ～ {original_df['開催日'].max().date()}"
            )
            sys.exit(1)

    # レースIDを作成
    results_df.insert(0, "レースID", results_df.apply(make_race_id, axis=1))

    print(f"前処理完了: {results_df.shape}")
    return results_df


def merge_programs_and_results(programs_df, results_df):
    """
    programs_dfとresults_dfをマージして着順情報を追加

    Args:
        programs_df: 番組表データ
        results_df: 結果データ

    Returns:
        pd.DataFrame: マージ済みのデータフレーム
    """
    print("=== データマージ中 ===")

    # レースIDと選手登番でマージ
    merged_df = programs_df.merge(
        results_df[["レースID", "選手登番", "着順"]],
        on=["レースID", "選手登番"],
        how="left",
    )

    print(f"マージ前のprograms_df形状: {programs_df.shape}")
    print(f"マージ後のmerged_df形状: {merged_df.shape}")

    # マージ結果の確認
    matched_count = merged_df["着順"].notna().sum()
    unmatched_count = merged_df["着順"].isna().sum()

    print(f"着順が取得できた件数: {matched_count}")
    print(f"着順が取得できなかった件数: {unmatched_count}")

    if unmatched_count > 0:
        match_rate = matched_count / (matched_count + unmatched_count) * 100
        print(f"マッチ率: {match_rate:.1f}%")

        if match_rate < 90:
            print(
                "警告: マッチ率が90%を下回っています。データの整合性を確認してください。"
            )

    return merged_df


def create_features(mode="train", start_date=None, end_date=None, output_path=None):
    """
    特徴量を作成するメイン関数

    Args:
        mode: 動作モード ("train" or "pred")
        start_date: 開始日 (YYYY-MM-DD形式)
        end_date: 終了日 (YYYY-MM-DD形式)
        output_path: 出力ファイルパス
    """
    # デフォルトの出力パスを設定
    if output_path is None:
        if mode == "train":
            output_path = "data/train.csv"
        elif mode == "pred":
            output_path = "data/pred.csv"
        else:
            raise ValueError(
                f"不正なモード: {mode}. 'train' または 'pred' を指定してください。"
            )

    try:
        # データ読み込みと前処理
        programs_df = load_and_preprocess_programs(
            "data/programs.csv", start_date, end_date
        )

        # 特徴量として必要なカラムを定義
        feature_columns = [
            "レースID",
            "枠番",
            "級別",
            "レース内全国勝率差",
            "レース内コース別1着率差",
            "レース内コース別複勝率差",
            "1着フラグ",
        ]

        if mode == "train":
            # 学習モード：結果データとマージして1着フラグを作成
            results_df = load_and_preprocess_results(
                "data/results.csv", start_date, end_date
            )
            # データマージ
            merged_df = merge_programs_and_results(programs_df, results_df)
            # 1着フラグ特徴量
            merged_df["1着フラグ"] = make_feature_first_place_flag(merged_df)
        elif mode == "pred":
            # 予測モード：番組データのみで特徴量を作成
            merged_df = programs_df.copy()

        # 必要なカラムのみを選択
        available_columns = [col for col in feature_columns if col in merged_df.columns]
        final_df = merged_df[available_columns]

        # 出力
        print(f"=== {output_path}として保存中 ===")
        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"特徴量作成完了!")
        print(f"モード: {mode}")
        print(f"出力ファイル: {output_path}")
        print(f"最終データ形状: {final_df.shape}")
        print(f"カラム数: {len(final_df.columns)}")
        print(f"データ期間: {start_date or '指定なし'} ～ {end_date or '指定なし'}")

        # 1着フラグの分布を確認（学習モードのみ）
        if mode == "train" and "1着フラグ" in final_df.columns:
            print("\n=== 1着フラグ分布 ===")
            flag_counts = final_df["1着フラグ"].value_counts().sort_index()
            print(flag_counts)
            if len(flag_counts) == 2:
                total_count = len(final_df)
                win_rate = flag_counts.get(1, 0) / total_count * 100
                print(f"1着率: {win_rate:.2f}%")

        return final_df

    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


def validate_date_format(date_string):
    """
    日付形式の妥当性をチェック

    Args:
        date_string: 日付文字列

    Returns:
        str: 妥当な場合はそのまま、無効な場合は例外を発生
    """
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"無効な日付形式: {date_string}. YYYY-MM-DD形式で入力してください。"
        )


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="競艇予測のための特徴量を作成します",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python create_features.py train 2025-01-01 2025-07-18    # 学習用データ作成（期間指定）
  python create_features.py train 2025-01-01               # 学習用データ作成（開始日のみ）
  python create_features.py train                          # 学習用データ作成（全期間）
  python create_features.py pred 2025-07-20                # 予測用データ作成
        """,
    )

    parser.add_argument(
        "mode",
        choices=["train", "pred"],
        help="動作モード ('train': 学習用データ作成, 'pred': 予測用データ作成)",
    )

    parser.add_argument(
        "start_date",
        nargs="?",
        type=validate_date_format,
        help="開始日 (YYYY-MM-DD形式、省略可)",
    )

    parser.add_argument(
        "end_date",
        nargs="?",
        type=validate_date_format,
        help="終了日 (YYYY-MM-DD形式、省略可)",
    )

    parser.add_argument(
        "--output",
        "-o",
        help="出力ファイルパス (デフォルト: train.csv または pred.csv)",
    )

    args = parser.parse_args()

    # 日付の妥当性チェック
    if args.start_date and args.end_date:
        start_dt = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(args.end_date, "%Y-%m-%d")

        if start_dt > end_dt:
            print("エラー: 開始日が終了日より後になっています")
            sys.exit(1)

    print("=== 競艇予測特徴量作成スクリプト ===")
    print(f"モード: {args.mode}")
    print(f"開始日: {args.start_date or '指定なし'}")
    print(f"終了日: {args.end_date or '指定なし'}")
    if args.output:
        print(f"出力ファイル: {args.output}")
    print()

    # 特徴量作成実行
    create_features(
        mode=args.mode,
        start_date=args.start_date,
        end_date=args.end_date,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
