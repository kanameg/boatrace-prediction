#!/usr/bin/env python3
"""
特徴量作成スクリプト

競艇予測のための特徴量を作成するスクリプトです。
開始日と終了日を指定して、該当期間のデータから特徴量を作成し、train.csvとして出力します。

使用方法:
    python create_features.py 2025-01-01 2025-07-18
    python create_features.py 2025-01-01           # 終了日指定なし
    python create_features.py                      # 全期間
"""

import argparse
import sys
from datetime import datetime

import numpy as np
import pandas as pd


def make_race_id(row):
    """
    年月日とレース場番号、レース番号から一意なIDを作成する関数

    Args:
        row: DataFrameの行データ

    Returns:
        int: レースID (YYYYMMDDPPRRR形式の整数)
    """
    date_str = f"{row['年']:04d}{row['月']:02d}{row['日']:02d}"
    place_str = f"{row['レース場番号']:02d}"
    race_str = f"{row['レース番号']:02d}"
    return int(f"{date_str}{place_str}{race_str}")


def grade_to_numeric(grade):
    """
    級別を数値に変換する関数

    Args:
        grade: 級別 (A1, A2, B1, B2)

    Returns:
        int: 数値化された級別 (A1:3, A2:2, B1:1, B2:0)
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

    # レースIDを作成
    programs_df.insert(0, "レースID", programs_df.apply(make_race_id, axis=1))

    # 級別を数値に変換
    programs_df["級別"] = programs_df["級別"].apply(grade_to_numeric)

    # 特徴量として必要なカラムのみを選択
    feature_columns = [
        "レースID",
        "枠番",
        "選手登番",
        "年齢",
        "体重",
        "級別",
        "全国勝率",
        "全国2連率",
        "当地勝率",
        "当地2連率",
        "モーター2連率",
        "ボート2連率",
    ]

    # 存在するカラムのみを選択
    available_columns = [col for col in feature_columns if col in programs_df.columns]
    programs_df = programs_df[available_columns]

    print(f"前処理完了: {programs_df.shape}")
    return programs_df


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


def create_features(start_date=None, end_date=None, output_path="data/train.csv"):
    """
    特徴量を作成するメイン関数

    Args:
        start_date: 開始日 (YYYY-MM-DD形式)
        end_date: 終了日 (YYYY-MM-DD形式)
        output_path: 出力ファイルパス
    """
    try:
        # データ読み込みと前処理
        programs_df = load_and_preprocess_programs(
            "data/programs.csv", start_date, end_date
        )
        results_df = load_and_preprocess_results(
            "data/results.csv", start_date, end_date
        )

        # データマージ
        merged_df = merge_programs_and_results(programs_df, results_df)

        # レースIDと選手登番を削除（特徴量としては不要）
        final_df = merged_df.drop(columns=["レースID", "選手登番"])

        # 出力
        print(f"=== {output_path}として保存中 ===")
        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")

        print(f"特徴量作成完了!")
        print(f"出力ファイル: {output_path}")
        print(f"最終データ形状: {final_df.shape}")
        print(f"カラム数: {len(final_df.columns)}")
        print(f"データ期間: {start_date or '指定なし'} ～ {end_date or '指定なし'}")

        # 着順の分布を確認
        if "着順" in final_df.columns:
            print("\n=== 着順分布 ===")
            print(final_df["着順"].value_counts().sort_index())

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
  python create_features.py 2025-01-01 2025-07-18    # 開始日と終了日を指定
  python create_features.py 2025-01-01               # 開始日のみ指定（終了日なし）
  python create_features.py                          # 全期間
        """,
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
        default="data/train.csv",
        help="出力ファイルパス (デフォルト: data/train.csv)",
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
    print(f"開始日: {args.start_date or '指定なし'}")
    print(f"終了日: {args.end_date or '指定なし'}")
    print(f"出力ファイル: {args.output}")
    print()

    # 特徴量作成実行
    create_features(
        start_date=args.start_date, end_date=args.end_date, output_path=args.output
    )


if __name__ == "__main__":
    main()
