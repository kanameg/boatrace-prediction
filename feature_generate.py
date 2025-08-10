import argparse
from datetime import datetime

import numpy as np
import pandas as pd


def make_race_id(row):
    """
    日付、レース場番号、レース番号から一意のレースIDを作成します。
    Args:
        row: DataFrameの行
    Returns:
        int: レースID（YYYYMMDDPPRRRの整数）
    """
    date_str = f"{row['年']:04d}{row['月']:02d}{row['日']:02d}"
    place_str = f"{row['レース場番号']:02d}"
    race_str = f"{row['レース番号']:02d}"
    return int(f"{date_str}{place_str}{race_str}")


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


def create_features(start_date, end_date):
    """
    特徴量を作成するメイン関数
    """
    # ここに特徴量作成のロジックを実装
    # programs.csvを読み込む
    programs_df = pd.read_csv("data/programs.csv", encoding="utf-8-sig")

    # racers.csvを読み込む
    racers_df = pd.read_csv("data/racers.csv", encoding="utf-8-sig")

    # 日付範囲でデータを絞り込む
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    # programs_dfの日付フィルタリング
    programs_df["日付"] = pd.to_datetime(
        programs_df["年"].astype(str)
        + "-"
        + programs_df["月"].astype(str).str.zfill(2)
        + "-"
        + programs_df["日"].astype(str).str.zfill(2)
    )
    mask = (programs_df["日付"] >= start_dt) & (programs_df["日付"] <= end_dt)
    programs_df = programs_df[mask]

    print(f"日付範囲 {start_date} から {end_date} でフィルタリング後:")
    print(f"programs データ件数: {len(programs_df):,} 件")

    if len(programs_df) == 0:
        print("警告: 指定された日付範囲にデータが存在しません。")
        return []

    # 必要な特徴量を計算
    features = []

    # レース内全国勝率差の特徴量を計算
    national_win_rate_diff_df = calculate_national_win_rate_diff(programs_df)
    features.append(("レース内全国勝率差", national_win_rate_diff_df))
    print("=== レース内全国勝率差 ===")
    print(national_win_rate_diff_df.shape)

    # レース内コース別1着率差の特徴量を計算
    course_win_rate_diff_df = calculate_course_win_rate_diff(programs_df, racers_df)
    features.append(("レース内コース別1着率差", course_win_rate_diff_df))
    print("=== レース内コース別1着率差 ===")
    print(course_win_rate_diff_df.shape)

    return features


# 以下は特徴量作成関数一覧


# 全国勝率差を計算する関数
def calculate_national_win_rate_diff(programs_df):
    """
    各レース内での全国勝率の平均からの差分を計算します。
    この関数は「レースID」列が存在しない場合は追加します。
    その後、各レースごとに「全国勝率」が平均からどれだけ離れているか（差分）を計算します。

    Args:
        programs_df (pd.DataFrame): programs.csvから読み込んだDataFrame。

    Returns:
        pd.DataFrame: 「レース内全国勝率差」列と、レースID、枠番を含むDataFrame。
    """
    df = programs_df.copy()

    # 「レースID」が存在しない場合は作成する
    if "レースID" not in df.columns:
        df["レースID"] = df.apply(make_race_id, axis=1)

    # 平均値との差分を計算する関数を定義
    def calc_rate_diff(rates):
        rates_numeric = pd.to_numeric(rates, errors="coerce")
        avg_rate = rates_numeric.mean()
        return np.round(rates_numeric - avg_rate, decimals=3)

    # 差分を計算
    df["レース内全国勝率差"] = df.groupby("レースID")["全国勝率"].transform(
        calc_rate_diff
    )
    df.sort_values(by=["レースID", "枠番"], inplace=True)

    return df[["レースID", "枠番", "レース内全国勝率差"]]


# レース内コース別1着率差を計算する関数
def calculate_course_win_rate_diff(programs_df, racers_df):
    """
    各レース内でのコース別1着率の平均からの差分を計算します。

    Args:
        programs_df (pd.DataFrame): programs.csvから読み込んだDataFrame
        racers_df (pd.DataFrame): racers.csvから読み込んだDataFrame

    Returns:
        pd.DataFrame: 「レース内コース別1着率差」列と、レースID、枠番を含むDataFrame
    """
    df = programs_df.copy()

    # 「レースID」が存在しない場合は作成する
    if "レースID" not in df.columns:
        df["レースID"] = df.apply(make_race_id, axis=1)

    # racers_dfから必要な情報を取得（選手登番をキーとして結合）
    # コース別1着率を計算する関数
    def calculate_course_win_rate(row):
        course = row["枠番"]  # 枠番をコースとして使用
        course_column_prefix = f"{course}コース"

        win_count_col = f"{course_column_prefix}1着回数"
        total_count_col = f"{course_column_prefix}進入回数"

        if win_count_col in racers_df.columns and total_count_col in racers_df.columns:
            racer_data = racers_df[racers_df["登番"] == row["選手登番"]]
            if not racer_data.empty:
                # 最近の選手データを利用するため末尾のデータ[-1]にアクセス
                win_count = racer_data.iloc[-1][win_count_col]
                total_count = racer_data.iloc[-1][total_count_col]

                # 数値型に変換し、0除算を避ける
                win_count = pd.to_numeric(win_count, errors="coerce")
                total_count = pd.to_numeric(total_count, errors="coerce")

                if pd.notna(win_count) and pd.notna(total_count) and total_count > 0:
                    return round(win_count / total_count, 4)

        return np.nan

    # 各選手のコース別1着率を計算
    df["コース別1着率"] = df.apply(calculate_course_win_rate, axis=1)

    # 平均値との差分を計算する関数を定義
    def calc_rate_diff(rates):
        rates_numeric = pd.to_numeric(rates, errors="coerce")
        # NaNを除いて平均を計算
        valid_rates = rates_numeric.dropna()
        if len(valid_rates) > 0:
            avg_rate = valid_rates.mean()
            return np.round(rates_numeric - avg_rate, decimals=4)
        else:
            return rates_numeric  # すべてNaNの場合はそのまま返す

    # レース内でのコース別1着率差を計算
    df["レース内コース別1着率差"] = df.groupby("レースID")["コース別1着率"].transform(
        calc_rate_diff
    )
    df.sort_values(by=["レースID", "枠番"], inplace=True)

    return df[["レースID", "枠番", "レース内コース別1着率差"]]


def main():
    parser = argparse.ArgumentParser(
        description="指定された日付範囲で特徴量を作成します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python feature_generate.py 2025-01-01 2025-07-18
        """,
    )

    parser.add_argument(
        "start_date",
        metavar="START_DATE",
        type=validate_date_format,
        help="開始日 (YYYY-MM-DD形式)",
    )

    parser.add_argument(
        "end_date",
        metavar="END_DATE",
        type=validate_date_format,
        help="終了日 (YYYY-MM-DD形式)",
    )

    args = parser.parse_args()

    # 日付の妥当性チェック
    start_dt = datetime.strptime(args.start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(args.end_date, "%Y-%m-%d")

    if start_dt > end_dt:
        print("エラー: 開始日が終了日より後になっています")
        exit(1)

    print("=== 特徴量生成スクリプト ===")
    print(f"開始日: {args.start_date}")
    print(f"終了日: {args.end_date}")
    print()

    # 特徴量作成実行
    features = create_features(
        start_date=args.start_date,
        end_date=args.end_date,
    )

    # 各特徴量をCSVファイルとして保存
    for feature_name, df in features:
        output_path = f"features/{feature_name}.csv"
        print(f"Saving {feature_name} to {output_path}")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\nすべての特徴量の保存が完了しました。")


if __name__ == "__main__":
    main()
