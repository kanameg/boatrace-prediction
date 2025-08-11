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
    date_str = f"{int(row['年']):04d}{int(row['月']):02d}{int(row['日']):02d}"
    place_str = f"{int(row['レース場番号']):02d}"
    race_str = f"{int(row['レース番号']):02d}"
    return int(f"{date_str}{place_str}{race_str}")


def validate_date_format(date_string):
    """
    日付形式の妥当性をチェック
    DateTimeに変換できるかを確認し、無効な場合は例外を発生させる。

    Args:
        date_string: 日付文字列

    Returns:
        str: 妥当な場合はそのまま、無効な場合は例外を発生
    """
    try:
        # strptimeでパースし、strftimeで再度フォーマットして元の文字列と比較
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        # if dt.strftime("%Y-%m-%d") != date_string:  # 2025-8-11のような0埋めなしは許容しない!
        #     raise ValueError
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"無効な日付形式: {date_string}. YYYY-MM-DD形式で入力してください。"
        )


def create_features(start_date, end_date):
    """
    特徴量を作成するメイン関数
    CSVデータを読み込んで、ここで各特徴量を作成する関数を呼び出す。

    Args:
        start_date (str): 開始日 (YYYY-MM-DD形式)
        end_date (str): 終了日 (YYYY-MM-DD形式)

    Returns:
        list: (特徴量名, DataFrame) のタプルのリスト
    """
    # ここに特徴量作成のロジックを実装
    # programs.csvを読み込む
    programs_df = pd.read_csv("data/programs.csv", encoding="utf-8-sig")

    # racers.csvを読み込む
    racers_df = pd.read_csv("data/racers.csv", encoding="utf-8-sig")

    # results.csvを読み込む
    results_df = pd.read_csv("data/results.csv", encoding="utf-8-sig")

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

    results_df["日付"] = pd.to_datetime(
        results_df["年"].astype(str)
        + "-"
        + results_df["月"].astype(str).str.zfill(2)
        + "-"
        + results_df["日"].astype(str).str.zfill(2)
    )
    mask = (results_df["日付"] >= start_dt) & (results_df["日付"] <= end_dt)
    results_df = results_df[mask]

    print(f"日付範囲 {start_date} から {end_date} でフィルタリング後:")
    print(f"programs データ件数: {len(programs_df):,} 件")
    print(f"results データ件数: {len(results_df):,} 件")

    if len(programs_df) == 0 or len(results_df) == 0:
        print("警告: 指定された日付範囲にデータが存在しません。")
        return []

    # 必要な特徴量を計算
    features = []

    # --------------------------------------------------------------------------------
    # レース内全国勝率差の特徴量を計算
    # --------------------------------------------------------------------------------
    national_win_rate_diff_df = calculate_national_win_rate_diff(programs_df)
    features.append(("レース内全国勝率差", national_win_rate_diff_df))
    print("=== レース内全国勝率差 ===")
    print(national_win_rate_diff_df.shape)

    # --------------------------------------------------------------------------------
    # レース内コース別1着率差の特徴量を計算
    # --------------------------------------------------------------------------------
    course_win_rate_diff_df = calculate_course_win_rate_diff(programs_df, racers_df)
    features.append(("レース内コース別1着率差", course_win_rate_diff_df))
    print("=== レース内コース別1着率差 ===")
    print(course_win_rate_diff_df.shape)

    # --------------------------------------------------------------------------------
    # レース内コース別平均スタートタイミング差の特徴量を計算
    # --------------------------------------------------------------------------------
    course_start_timing_diff_df = calculate_course_start_timing_diff(
        programs_df, racers_df
    )
    features.append(
        ("レース内コース別平均スタートタイミング差", course_start_timing_diff_df)
    )
    print("=== レース内コース別平均スタートタイミング差 ===")
    print(course_start_timing_diff_df.shape)

    # --------------------------------------------------------------------------------
    # 1着フラグの特徴量を計算（results.csvの着順データから）
    # --------------------------------------------------------------------------------
    if "着順" in results_df.columns:
        first_place_flag_df = calculate_first_place(programs_df, results_df)
        if first_place_flag_df is not None and not first_place_flag_df.empty:
            features.append(("1着フラグ", first_place_flag_df))
            print("=== 1着フラグ ===")
            print(first_place_flag_df.shape)

    return features


# --------------------------------------------------------------------------------
# 以下は特徴量作成関数一覧
# --------------------------------------------------------------------------------


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
    col_name = "レース内全国勝率差"  # 特徴量名
    sort_col_name = ["レースID", "枠番"]  # ソートに使用する列名
    df = programs_df.copy()

    # 「レースID」が存在しない場合は作成する
    if "レースID" not in df.columns:
        df["レースID"] = df.apply(make_race_id, axis=1)

    # 平均値との差分を計算する関数を定義 (TODO: 共通化可能)
    def calc_rate_diff(rates):
        rates_numeric = pd.to_numeric(rates, errors="coerce")
        avg_rate = rates_numeric.mean()
        return np.round(rates_numeric - avg_rate, decimals=3)

    # 差分を計算
    df[col_name] = df.groupby("レースID")["全国勝率"].transform(calc_rate_diff)
    # 全データで並びが崩れないようにソート(レースIDと枠番)
    df.sort_values(by=sort_col_name, inplace=True)

    return df[sort_col_name + [col_name]]


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
    col_name = "レース内コース別1着率差"  # 特徴量名
    sort_col_name = ["レースID", "枠番"]  # ソートに使用する列名
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
                else:
                    # データがないまたは、0除算になる場合は0.0f
                    return 0.0

        # 選手情報がない場合のみNaN
        return np.nan

    # 各選手のコース別1着率を計算
    df["コース別1着率"] = df.apply(calculate_course_win_rate, axis=1)

    # 平均値との差分を計算する関数を定義 (TODO: 共通化可能)
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
    df[col_name] = df.groupby("レースID")["コース別1着率"].transform(calc_rate_diff)
    # 全データで並びが崩れないようにソート(レースIDと枠番)
    df.sort_values(by=sort_col_name, inplace=True)

    return df[sort_col_name + [col_name]]


# レース内コース別平均スタートタイミング差を計算する関数
def calculate_course_start_timing_diff(programs_df, racers_df):
    """
    各レース内でのコース別平均スタートタイミングの平均からの差分を計算します。

    Args:
        programs_df (pd.DataFrame): programs.csvから読み込んだDataFrame
        racers_df (pd.DataFrame): racers.csvから読み込んだDataFrame

    Returns:
        pd.DataFrame: 「レース内コース別平均スタートタイミング差」列と、レースID、枠番を含むDataFrame
    """
    col_name = "レース内コース別平均スタートタイミング差"  # 特徴量名
    sort_col_name = ["レースID", "枠番"]  # ソートに使用する列名
    df = programs_df.copy()

    # 「レースID」が存在しない場合は作成する
    if "レースID" not in df.columns:
        df["レースID"] = df.apply(make_race_id, axis=1)

    # racers_dfから必要な情報を取得（選手登番をキーとして結合）
    # コース別平均スタートタイミングを計算する関数
    def calculate_course_start_timing(row):
        course = row["枠番"]  # 枠番をコースとして使用
        start_timing_col = f"{course}コース平均スタートタイミング"

        if start_timing_col in racers_df.columns:
            racer_data = racers_df[racers_df["登番"] == row["選手登番"]]
            if not racer_data.empty:
                # 最近の選手データを利用するため末尾のデータ[-1]にアクセス
                start_timing = racer_data.iloc[-1][start_timing_col]

                # 数値型に変換
                start_timing = pd.to_numeric(start_timing, errors="coerce")

                if pd.notna(start_timing):
                    return round(start_timing, 3)
                else:
                    # データがない場合は0.0f
                    return 0.0

        # 選手情報がない場合のみNaN
        return np.nan

    # 各選手のコース別平均スタートタイミングを計算
    df["コース別平均スタートタイミング"] = df.apply(
        calculate_course_start_timing, axis=1
    )

    # 平均値との差分を計算する関数を定義 (TODO: 共通化可能)
    def calc_timing_diff(timings):
        timings_numeric = pd.to_numeric(timings, errors="coerce")
        # NaNを除いて平均を計算
        valid_timings = timings_numeric.dropna()
        if len(valid_timings) > 0:
            avg_timing = valid_timings.mean()
            return np.round(timings_numeric - avg_timing, decimals=3)
        else:
            return timings_numeric  # すべてNaNの場合はそのまま返す

    # レース内でのコース別平均スタートタイミング差を計算
    df[col_name] = df.groupby("レースID")["コース別平均スタートタイミング"].transform(
        calc_timing_diff
    )
    # 全データで並びが崩れないようにソート(レースIDと枠番)
    df.sort_values(by=sort_col_name, inplace=True)

    return df[sort_col_name + [col_name]]


# 1着フラグを計算する関数
def calculate_first_place(programs_df, results_df):
    """
    results.csvの着順データから1着フラグを作成します。

    Args:
        programs_df (pd.DataFrame): programs.csvから読み込んだDataFrame
        results_df (pd.DataFrame): results.csvから読み込んだDataFrame

    Returns:
        pd.DataFrame: 「1着フラグ」列と、レースID、枠番を含むDataFrame
    """
    if "着順" not in results_df.columns:
        print(
            "警告: results.csvに「着順」列が存在しません。1着フラグは作成されません。"
        )
        return None

    col_name = "1着フラグ"  # 特徴量名
    sort_col_name = ["レースID", "枠番"]  # ソートに使用する列名

    # programs_dfからベースとなるDataFrameを作成
    df = programs_df.copy()

    # 「レースID」が存在しない場合は作成する
    if "レースID" not in df.columns:
        df["レースID"] = df.apply(make_race_id, axis=1)

    # results_dfにもレースIDを作成
    results_with_race_id = results_df.copy()
    if "レースID" not in results_with_race_id.columns:
        results_with_race_id["レースID"] = results_with_race_id.apply(
            make_race_id, axis=1
        )

    # results_dfから1着フラグを作成（着順が1の場合は1、それ以外は0）
    results_with_race_id = results_with_race_id.copy()  # コピーを明示的に作成
    results_with_race_id[col_name] = (
        results_with_race_id["着順"].astype(str) == "1"
    ).astype(int)

    # programs_dfとresults_dfをレースID、枠番（艇番）でマージ
    # 注意: programs.csvは「枠番」、results.csvは「艇番」の列名
    merge_df = df.merge(
        results_with_race_id[["レースID", "艇番", col_name]],
        left_on=["レースID", "枠番"],
        right_on=["レースID", "艇番"],
        how="left",
    )

    # マージできなかった場合は0で埋める
    merge_df[col_name] = merge_df[col_name].fillna(0).astype(int)

    # 不要な列を削除（艇番列）
    if "艇番" in merge_df.columns:
        merge_df = merge_df.drop("艇番", axis=1)

    # 全データで並びが崩れないようにソート(レースIDと枠番)
    merge_df.sort_values(by=sort_col_name, inplace=True)

    return merge_df[sort_col_name + [col_name]]


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
    )  # 特徴量情報(名前とデータフレーム名)

    # 各特徴量をCSVファイルとして保存
    for feature_name, df in features:
        output_path = f"features/{feature_name}.csv"
        print(f"Saving {feature_name} to {output_path}")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\nすべての特徴量の保存が完了しました。")


if __name__ == "__main__":
    main()
