#!/usr/bin/env python3
"""
学習データ作成プログラム

このプログラムは、競艇のレース結果データを基に、選手やレースの特徴を抽出し、
機械学習モデルの学習に使用するデータセットを作成します。
"""

import argparse
import os
import sys
from datetime import datetime

import pandas as pd


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="競艇学習データ作成プログラム")

    parser.add_argument(
        "mode",
        choices=["train", "test"],
        help="データ種別 (train: 学習用, test: テスト用)",
    )
    parser.add_argument("start_year", type=int, help="開始年 (YYYY)")
    parser.add_argument("start_month", type=int, help="開始月 (MM)")
    parser.add_argument("start_day", type=int, help="開始日 (DD)")
    parser.add_argument("end_year", type=int, nargs="?", help="終了年 (YYYY) - 省略可")
    parser.add_argument("end_month", type=int, nargs="?", help="終了月 (MM) - 省略可")
    parser.add_argument("end_day", type=int, nargs="?", help="終了日 (DD) - 省略可")
    parser.add_argument(
        "race_track",
        type=int,
        nargs="?",
        help="レース場番号 (1-24) - 省略可、省略時は全レース場",
    )

    args = parser.parse_args()

    # 終了日が省略された場合は開始日と同じにする
    if args.end_year is None:
        args.end_year = args.start_year
        args.end_month = args.start_month
        args.end_day = args.start_day

    return args


def validate_date(year, month, day):
    """日付の妥当性をチェックする"""
    try:
        datetime(year, month, day)
        return True
    except ValueError:
        return False


def load_race_data(file_path="data/racer_program.csv"):
    """レース結果データを読み込む"""
    try:
        print(f"データファイルを読み込んでいます: {file_path}")
        df = pd.read_csv(file_path)
        print(f"データ読み込み完了: {len(df)}行のデータ")
        return df
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: データファイルの読み込みに失敗しました - {e}")
        sys.exit(1)


def filter_by_date(
    df, start_year, start_month, start_day, end_year, end_month, end_day
):
    """指定された日付範囲でデータをフィルタリングする"""
    # データのコピーを作成
    df = df.copy()

    # 年月日を文字列として結合してからdatetimeに変換
    df["日付文字列"] = (
        df["年"].astype(str)
        + "-"
        + df["月"].astype(str).str.zfill(2)
        + "-"
        + df["日"].astype(str).str.zfill(2)
    )
    df["日付"] = pd.to_datetime(df["日付文字列"], format="%Y-%m-%d", errors="coerce")

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    print(
        f"日付範囲でフィルタリング: {start_date.strftime('%Y-%m-%d')} ～ {end_date.strftime('%Y-%m-%d')}"
    )

    filtered_df = df[(df["日付"] >= start_date) & (df["日付"] <= end_date)]
    print(f"フィルタリング後: {len(filtered_df)}行のデータ")

    # 一時的な列を削除
    filtered_df = filtered_df.drop(["日付文字列", "日付"], axis=1)

    return filtered_df


def filter_by_race_track(df, race_track):
    """指定されたレース場でデータをフィルタリングする"""
    if race_track is not None:
        print(f"レース場番号 {race_track} でフィルタリング")
        filtered_df = df[df["レース場番号"] == race_track]
        print(f"フィルタリング後: {len(filtered_df)}行のデータ")
        return filtered_df
    else:
        print("全レース場のデータを使用")
        return df


def extract_features(df):
    """必要な特徴量を抽出する"""
    print("選手情報の特徴量を抽出中...")

    # 仕様書で指定された列を抽出（日付情報を含める）
    # 注意: '性別'はデータに含まれていないため除外
    required_columns = [
        "年",  # 日付情報
        "月",  # 日付情報
        "日",  # 日付情報
        "枠番",
        "選手登番",
        "年齢",
        "体重",
        "級別",
        "全国勝率",
        "モーター2連率",
        "ボート2連率",
        "着順",  # 予測対象
        "勝敗",  # 予測対象（バイナリ）
    ]

    # 利用可能な列のみを選択
    available_columns = [col for col in required_columns if col in df.columns]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"警告: 以下の列がデータに含まれていません: {missing_columns}")

    feature_df = df[available_columns].copy()

    # データ型の確認と変換
    numeric_columns = [
        "年齢",
        "体重",
        "全国勝率",
        "モーター2連率",
        "ボート2連率",
        "着順",
    ]
    for col in numeric_columns:
        if col in feature_df.columns:
            feature_df[col] = pd.to_numeric(feature_df[col], errors="coerce")

    print(f"特徴量抽出完了: {len(feature_df)}行、{len(feature_df.columns)}列")
    print(f"抽出された列: {list(feature_df.columns)}")

    return feature_df


def save_data(df, mode, output_dir="data/"):
    """データをCSVファイルとして保存する"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, f"{mode}.csv")

    print(f"データを保存中: {output_file}")
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"保存完了: {len(df)}行のデータを {output_file} に保存しました")


def print_data_summary(df, mode):
    """データの概要を表示する"""
    print(f"\n=== {mode.upper()}データの概要 ===")
    print(f"データ数: {len(df)}行")

    # 日付情報が含まれている場合は期間を表示
    if all(col in df.columns for col in ["年", "月", "日"]):
        print(
            f"期間: {df['年'].min()}/{df['月'].min()}/{df['日'].min()} ～ {df['年'].max()}/{df['月'].max()}/{df['日'].max()}"
        )

    if "レース場番号" in df.columns:
        race_tracks = sorted(df["レース場番号"].unique())
        print(f"レース場: {race_tracks}")

    if "級別" in df.columns:
        grade_counts = df["級別"].value_counts()
        print(f"級別分布:\n{grade_counts}")

    if "着順" in df.columns:
        rank_counts = df["着順"].value_counts().sort_index()
        print(f"着順分布:\n{rank_counts}")

    # 欠損値の確認
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print(f"欠損値:\n{missing_data[missing_data > 0]}")


def main():
    """メイン処理"""
    print("競艇学習データ作成プログラム開始")

    # コマンドライン引数の解析
    args = parse_arguments()

    # 日付の妥当性チェック
    if not validate_date(args.start_year, args.start_month, args.start_day):
        print("エラー: 開始日が無効です")
        sys.exit(1)

    if not validate_date(args.end_year, args.end_month, args.end_day):
        print("エラー: 終了日が無効です")
        sys.exit(1)

    # データの読み込み
    df = load_race_data()

    # 日付範囲でフィルタリング
    df = filter_by_date(
        df,
        args.start_year,
        args.start_month,
        args.start_day,
        args.end_year,
        args.end_month,
        args.end_day,
    )

    # レース場でフィルタリング
    df = filter_by_race_track(df, args.race_track)

    # データが空でないかチェック
    if len(df) == 0:
        print("エラー: 指定された条件に一致するデータがありません")
        sys.exit(1)

    # 特徴量の抽出
    feature_df = extract_features(df)

    # データの概要を表示
    print_data_summary(feature_df, args.mode)

    # データの保存
    save_data(feature_df, args.mode)

    print(f"\n{args.mode}データの作成が完了しました")


if __name__ == "__main__":
    main()
