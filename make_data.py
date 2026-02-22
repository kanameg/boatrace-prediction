#!/usr/bin/env python3
"""ボートレース予測用特徴量データ作成プログラム

Usage:
  # 学習データ生成
  python make_data.py train --start 2025-01-01 --end 2025-12-31

  # 予測データ生成
  python make_data.py pred --date 2026-02-22
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# --- 定数 ---
DATA_DIR = Path("data")
OUTPUT_DIR = DATA_DIR / "processed"

PROGRAMS_CSV = DATA_DIR / "programs.csv"
RESULTS_CSV = DATA_DIR / "results.csv"
RACERS_CSV = DATA_DIR / "racers.csv"

TRAIN_OUTPUT = OUTPUT_DIR / "train_data.csv"
PRED_OUTPUT = OUTPUT_DIR / "pred_data.csv"

# 着順除外リスト（フライング・失格）
INVALID_ORDER = {"F", "S0", "S1", "S2", "L0", "L1", "K0", "K1"}

# 級別 → 数値コード
CLASS_CODE = {"A1": 4, "A2": 3, "B1": 2, "B2": 1}


# ---------------------------------------------------------------------------
# 共通ユーティリティ
# ---------------------------------------------------------------------------

def make_race_id(df: pd.DataFrame) -> pd.Series:
    """年・月・日・レース場番号・レース番号から12桁のレースID（文字列）を生成"""
    return (
        df["年"].astype(str)
        + df["月"].astype(str).str.zfill(2)
        + df["日"].astype(str).str.zfill(2)
        + df["レース場番号"].astype(str).str.zfill(2)
        + df["レース番号"].astype(str).str.zfill(2)
    ).astype(str)


def make_date_col(df: pd.DataFrame) -> pd.Series:
    """年・月・日列からdatetime型の開催日を生成"""
    return pd.to_datetime(
        df["年"].astype(str)
        + "-"
        + df["月"].astype(str)
        + "-"
        + df["日"].astype(str)
    )


def add_race_diff(df: pd.DataFrame, src_col: str, dst_col: str) -> pd.DataFrame:
    """レース内平均との差を新カラムとして追加"""
    df[dst_col] = df.groupby("レースID")[src_col].transform(lambda x: x - x.mean())
    return df


def time_to_seconds(time_str: str) -> float:
    """レースタイム文字列（分.秒.1/10秒）を秒に変換"""
    try:
        parts = str(time_str).split(".")
        return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 10
    except Exception:
        return np.nan


def load_racers_latest(path: Path) -> pd.DataFrame:
    """
    racers.csv を読み込み、各選手の最新レコードを返す。
    racers.csv には同一選手の複数年・複数期のデータが含まれるため、
    年・期が最大のレコード（最新データ）を選手登番ごとに1件だけ使用する。
    """
    df = pd.read_csv(path)
    # 登番 → 選手登番 に統一
    df = df.rename(columns={"登番": "選手登番"})
    # 年・期で降順ソートし、選手登番ごとに先頭1件（最新）を残す
    df = (
        df.sort_values(["年", "期"], ascending=False)
        .drop_duplicates(subset="選手登番", keep="first")
        .reset_index(drop=True)
    )
    return df


def build_program_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    programs.csv 由来のカラムからレース内差分特徴量を作成する。
    df には レースID・艇番・各統計カラムが含まれること。
    """
    df = df.copy()

    # 級別 → 数値コード
    df["級別コード"] = df["級別"].map(CLASS_CODE)

    # レース内平均との差分特徴量
    for src, dst in [
        ("全国勝率",    "全国勝率差"),
        ("全国2連率",   "全国2連率差"),
        ("当地勝率",    "当地勝率差"),
        ("当地2連率",   "当地2連率差"),
        ("モーター2連率", "モーター2連率差"),
        ("ボート2連率",  "ボート2連率差"),
        ("級別コード",  "級別差"),
    ]:
        df = add_race_diff(df, src, dst)

    return df


def add_course_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    艇番に対応するコース別複勝率・コース別ST差を付与する。
    df には {N}コース複勝率 と {N}コース平均スタートタイミング が含まれること。
    """
    df["コース別複勝率"] = np.nan
    df["コース別ST"] = np.nan

    for n in range(1, 7):
        mask = df["艇番"] == n
        fukusho_col = f"{n}コース複勝率"
        st_col = f"{n}コース平均スタートタイミング"
        if fukusho_col in df.columns:
            df.loc[mask, "コース別複勝率"] = df.loc[mask, fukusho_col]
        if st_col in df.columns:
            df.loc[mask, "コース別ST"] = df.loc[mask, st_col]

    # コース別ST差 = コース別ST - レース内平均コース別ST
    df = add_race_diff(df, "コース別ST", "コース別ST差")

    # 不要な中間カラムを削除
    drop_cols = (
        [f"{n}コース複勝率" for n in range(1, 7)]
        + [f"{n}コース平均スタートタイミング" for n in range(1, 7)]
        + ["コース別ST"]
    )
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    return df


# ---------------------------------------------------------------------------
# 学習用データ生成
# ---------------------------------------------------------------------------

def build_train(start_date: str, end_date: str) -> None:
    print(f"[train] 期間: {start_date} 〜 {end_date}")

    # --- results.csv 読み込み ---
    print("results.csv を読み込み中...")
    results = pd.read_csv(RESULTS_CSV)
    results.insert(0, "開催日", make_date_col(results))
    results.insert(1, "レースID", make_race_id(results))

    # 距離・期間フィルタ
    results = results[results["距離"] == 1800]
    results = results[
        (results["開催日"] >= pd.to_datetime(start_date))
        & (results["開催日"] <= pd.to_datetime(end_date))
    ]

    # フライング・失格を除外し、着順を整数に変換
    results = results[~results["着順"].astype(str).isin(INVALID_ORDER)]
    results["着順"] = results["着順"].astype(int)

    # 進入を数値に変換
    results["進入"] = pd.to_numeric(results["進入"], errors="coerce")

    # --- programs.csv 読み込みとマージ ---
    print("programs.csv を読み込み中...")
    programs = pd.read_csv(PROGRAMS_CSV)
    programs.insert(0, "開催日", make_date_col(programs))
    programs.insert(1, "レースID", make_race_id(programs))
    programs = programs[programs["距離"] == 1800]
    programs = programs.rename(columns={"枠番": "艇番"})

    prog_cols = [
        "レースID", "選手登番", "艇番",
        "全国勝率", "全国2連率", "当地勝率", "当地2連率",
        "モーター2連率", "ボート2連率", "級別",
    ]
    result_cols = [
        "レースID", "選手登番", "艇番", "着順",
    ]

    df = results[result_cols].merge(
        programs[prog_cols],
        on=["レースID", "選手登番", "艇番"],
        how="left",
    )

    # --- プログラム由来特徴量 ---
    df = build_program_features(df)

    # --- racers.csv マージ（最新レコードのみ使用）---
    print("racers.csv を読み込み中（最新レコード使用）...")
    racers = load_racers_latest(RACERS_CSV)
    racer_cols = (
        ["選手登番", "今期能力指数", "平均スタートタイミング"]
        + [f"{n}コース複勝率" for n in range(1, 7)]
        + [f"{n}コース平均スタートタイミング" for n in range(1, 7)]
    )
    df = df.merge(racers[racer_cols], on="選手登番", how="left")

    # 能力指数差・平均ST差
    df = add_race_diff(df, "今期能力指数", "能力指数差")
    df = add_race_diff(df, "平均スタートタイミング", "平均ST差")

    # コース別統計（艇番に対応するコース別複勝率・ST差）
    df = add_course_stats(df)

    # --- 目的変数 ---
    df["1着フラグ"] = (df["着順"] == 1).astype(int)

    # --- 出力カラム整理 ---
    out_cols = [
        "レースID", "選手登番", "艇番",
        "全国勝率差", "全国2連率差", "当地勝率差", "当地2連率差",
        "モーター2連率差", "ボート2連率差", "級別差",
        "能力指数差", "平均ST差",
        "コース別複勝率", "コース別ST差",
        "1着フラグ",
    ]
    df = df[out_cols]

    # --- 保存 ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(TRAIN_OUTPUT, index=False)
    print(f"保存完了: {TRAIN_OUTPUT}  ({len(df):,} 行)")


# ---------------------------------------------------------------------------
# 予測用データ生成
# ---------------------------------------------------------------------------

def build_pred(pred_date: str) -> None:
    print(f"[pred] 予測日: {pred_date}")

    # --- programs.csv 読み込み ---
    print("programs.csv を読み込み中...")
    programs = pd.read_csv(PROGRAMS_CSV)
    programs.insert(0, "開催日", make_date_col(programs))
    programs.insert(1, "レースID", make_race_id(programs))
    programs = programs[programs["距離"] == 1800]
    programs = programs.rename(columns={"枠番": "艇番"})

    # 日付フィルタ
    df = programs[programs["開催日"] == pd.to_datetime(pred_date)].copy()
    if df.empty:
        print(f"警告: {pred_date} のデータが見つかりません。")
        return

    # --- プログラム由来特徴量 ---
    df = build_program_features(df)

    # --- racers.csv マージ（最新レコードのみ使用）---
    print("racers.csv を読み込み中（最新レコード使用）...")
    racers = load_racers_latest(RACERS_CSV)
    racer_cols = (
        ["選手登番", "今期能力指数", "平均スタートタイミング"]
        + [f"{n}コース複勝率" for n in range(1, 7)]
        + [f"{n}コース平均スタートタイミング" for n in range(1, 7)]
    )
    df = df.merge(racers[racer_cols], on="選手登番", how="left")

    # 能力指数差・平均ST差
    df = add_race_diff(df, "今期能力指数", "能力指数差")
    df = add_race_diff(df, "平均スタートタイミング", "平均ST差")

    # コース別統計
    df = add_course_stats(df)

    # --- 出力カラム整理 ---
    out_cols = [
        "レースID", "選手登番", "艇番",
        "全国勝率差", "全国2連率差", "当地勝率差", "当地2連率差",
        "モーター2連率差", "ボート2連率差", "級別差",
        "能力指数差", "平均ST差",
        "コース別複勝率", "コース別ST差",
    ]
    df = df[out_cols]

    # --- 保存 ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PRED_OUTPUT, index=False)
    print(f"保存完了: {PRED_OUTPUT}  ({len(df):,} 行)")


# ---------------------------------------------------------------------------
# エントリーポイント
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="ボートレース予測用特徴量データ作成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # train サブコマンド
    train_p = subparsers.add_parser("train", help="学習用データを生成する")
    train_p.add_argument("--start", required=True, metavar="YYYY-MM-DD", help="開始日")
    train_p.add_argument("--end",   required=True, metavar="YYYY-MM-DD", help="終了日")

    # pred サブコマンド
    pred_p = subparsers.add_parser("pred", help="予測用データを生成する")
    pred_p.add_argument("--date", required=True, metavar="YYYY-MM-DD", help="予測対象日")

    args = parser.parse_args()

    if args.mode == "train":
        build_train(args.start, args.end)
    elif args.mode == "pred":
        build_pred(args.date)


if __name__ == "__main__":
    main()
