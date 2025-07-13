#!/usr/bin/env python3
"""
勝敗予測プログラム

このプログラムは、競艇の勝敗を予測するランダムフォレストモデルを
作成・学習・予測するためのプログラムです。
"""

import argparse
import json
import os
import pickle
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(description="競艇勝敗予測プログラム")

    parser.add_argument(
        "mode",
        nargs="?",
        choices=["train", "predict"],
        help="実行モード (train: 学習, predict: 予測, 省略時: 両方実行)",
    )
    parser.add_argument("start_train_date", nargs="?", help="学習開始日 (YYYY-MM-DD)")
    parser.add_argument("end_train_date", nargs="?", help="学習終了日 (YYYY-MM-DD)")
    parser.add_argument("start_test_date", nargs="?", help="評価開始日 (YYYY-MM-DD)")
    parser.add_argument(
        "end_test_date", nargs="?", help="評価終了日 (YYYY-MM-DD) - 省略可"
    )

    return parser.parse_args()


def load_data(file_path):
    """データを読み込む"""
    try:
        print(f"データを読み込んでいます: {file_path}")
        df = pd.read_csv(file_path)
        print(f"データ読み込み完了: {len(df)}行")
        return df
    except FileNotFoundError:
        print(f"エラー: ファイル '{file_path}' が見つかりません")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: データの読み込みに失敗しました - {e}")
        sys.exit(1)


def filter_by_date_range(df, start_date_str, end_date_str):
    """指定された日付範囲でデータをフィルタリングする"""
    if not start_date_str or not end_date_str:
        return df

    try:
        # 日付文字列をdatetimeオブジェクトに変換
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # データフレームの日付列を結合してdatetimeに変換
        df_copy = df.copy()
        df_copy["日付文字列"] = (
            df_copy["年"].astype(str)
            + "-"
            + df_copy["月"].astype(str).str.zfill(2)
            + "-"
            + df_copy["日"].astype(str).str.zfill(2)
        )
        df_copy["日付"] = pd.to_datetime(df_copy["日付文字列"], format="%Y-%m-%d")

        # 日付範囲でフィルタリング
        filtered_df = df_copy[
            (df_copy["日付"] >= start_date) & (df_copy["日付"] <= end_date)
        ]

        # 一時的な列を削除
        filtered_df = filtered_df.drop(["日付文字列", "日付"], axis=1)

        print(f"日付フィルタリング: {start_date_str} ～ {end_date_str}")
        print(f"フィルタリング後: {len(filtered_df)}行")

        return filtered_df

    except ValueError as e:
        print(f"警告: 日付形式が正しくありません ({e})")
        return df
    except Exception as e:
        print(f"警告: 日付フィルタリング中にエラーが発生しました ({e})")
        return df


def prepare_features(df):
    """特徴量を準備する"""
    print("特徴量を準備中...")

    # 仕様書で指定された特徴量（日付列は除外）
    feature_columns = [
        "枠番",
        "選手登番",
        "年齢",
        "体重",
        "級別",
        "全国勝率",
        "モーター2連率",
        "ボート2連率",
    ]

    # 特徴量のみを抽出
    features_df = df[feature_columns].copy()

    # 級別をエンコーディング
    if "級別" in features_df.columns:
        grade_mapping = {"A1": 4, "A2": 3, "B1": 2, "B2": 1}
        features_df["級別"] = features_df["級別"].map(grade_mapping)

    # 欠損値の処理
    features_df = features_df.fillna(features_df.mean())

    print(f"特徴量準備完了: {len(features_df)}行、{len(features_df.columns)}列")
    print(f"使用する特徴量: {list(features_df.columns)}")

    return features_df


def train_model(X_train, y_train):
    """ランダムフォレストモデルを学習する"""
    print("ランダムフォレストモデルを学習中...")

    # ランダムフォレストモデルの作成
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
    )

    # モデルの学習
    model.fit(X_train, y_train)

    print("モデル学習完了")
    return model


def evaluate_model(model, X_test, y_test):
    """モデルを評価する"""
    print("モデルを評価中...")

    # 予測実行
    y_pred = model.predict(X_test)

    # 評価指標の計算
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="binary", zero_division=0)
    recall = recall_score(y_test, y_pred, average="binary", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="binary", zero_division=0)

    # 結果の表示
    results = {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
    }

    print("=== モデル評価結果 ===")
    print(json.dumps(results, indent=2))

    return results


def save_model(model, file_path="model/random_forest_model.pkl"):
    """学習済みモデルを保存する"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        pickle.dump(model, f)

    print(f"モデルを保存しました: {file_path}")


def load_model(file_path="model/random_forest_model.pkl"):
    """学習済みモデルを読み込む"""
    try:
        with open(file_path, "rb") as f:
            model = pickle.load(f)
        print(f"モデルを読み込みました: {file_path}")
        return model
    except FileNotFoundError:
        print(f"エラー: モデルファイル '{file_path}' が見つかりません")
        print("先にtrainコマンドでモデルを学習してください")
        sys.exit(1)


def predict_results(model, test_data):
    """予測を実行する"""
    print("予測を実行中...")

    # 特徴量の準備
    X_test = prepare_features(test_data)

    # 予測実行
    predictions = model.predict(X_test)

    print(f"予測完了: {len(predictions)}件の予測結果")

    return predictions


def save_predictions(test_data, predictions, output_file="predict_results.csv"):
    """予測結果を保存する"""
    print(f"予測結果を保存中: {output_file}")

    # テストデータのコピーを作成
    result_df = test_data.copy()

    # 予測結果を最終列に追加
    result_df["予測勝敗"] = predictions

    # CSVファイルに保存
    result_df.to_csv(output_file, index=False, encoding="utf-8")

    print(f"予測結果を保存しました: {output_file}")

    # 予測結果の概要を表示
    win_predictions = sum(predictions)
    total_predictions = len(predictions)
    print(f"予測概要: 勝ち予測 {win_predictions}件 / 全体 {total_predictions}件")

    # 日付範囲を表示（日付情報がある場合）
    if all(col in result_df.columns for col in ["年", "月", "日"]):
        min_date = (
            f"{result_df['年'].min()}/{result_df['月'].min()}/{result_df['日'].min()}"
        )
        max_date = (
            f"{result_df['年'].max()}/{result_df['月'].max()}/{result_df['日'].max()}"
        )
        print(f"予測対象期間: {min_date} ～ {max_date}")


def run_train_mode(args):
    """学習モードを実行する"""
    print("=== 学習モード実行 ===")

    # データの読み込み
    train_data = load_data("data/train.csv")

    # 欠損値のある行を除外（勝敗が不明な行）
    train_data = train_data.dropna(subset=["勝敗"])

    # 元データをバックアップ（評価データ用）
    original_data = train_data.copy()

    # 学習用データの日付フィルタリング
    if args.start_train_date and args.end_train_date:
        train_data = filter_by_date_range(
            train_data, args.start_train_date, args.end_train_date
        )
        if len(train_data) == 0:
            print("エラー: 指定された学習期間にデータがありません")
            sys.exit(1)

    # 評価用データの準備
    eval_data = train_data.copy()  # デフォルトは学習データと同じ

    # 評価期間が指定されている場合
    if args.start_test_date:
        eval_end_date = (
            args.end_test_date if args.end_test_date else args.start_test_date
        )
        eval_data = filter_by_date_range(
            original_data, args.start_test_date, eval_end_date
        )
        if len(eval_data) == 0:
            print("エラー: 指定された評価期間にデータがありません")
            sys.exit(1)

        # 学習データから評価期間のデータを除外
        eval_data_with_dates = eval_data.copy()
        eval_data_with_dates["日付文字列"] = (
            eval_data_with_dates["年"].astype(str)
            + "-"
            + eval_data_with_dates["月"].astype(str).str.zfill(2)
            + "-"
            + eval_data_with_dates["日"].astype(str).str.zfill(2)
        )
        eval_dates_set = set(eval_data_with_dates["日付文字列"])

        train_data_with_dates = train_data.copy()
        train_data_with_dates["日付文字列"] = (
            train_data_with_dates["年"].astype(str)
            + "-"
            + train_data_with_dates["月"].astype(str).str.zfill(2)
            + "-"
            + train_data_with_dates["日"].astype(str).str.zfill(2)
        )

        train_data = train_data[
            ~train_data_with_dates["日付文字列"].isin(eval_dates_set)
        ]

        print(f"学習期間と評価期間を分離しました")
        print(f"学習データ: {len(train_data)}行")
        print(f"評価データ: {len(eval_data)}行")

        # 特徴量と目的変数の準備
        X_train = prepare_features(train_data)
        y_train = train_data["勝敗"].astype(int)
        X_test = prepare_features(eval_data)
        y_test = eval_data["勝敗"].astype(int)

    else:
        # 評価期間が指定されていない場合はランダム分割
        print("評価期間が指定されていないため、ランダム分割を使用します")
        X = prepare_features(train_data)
        y = train_data["勝敗"].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

    print(f"最終学習データ: {len(X_train)}行, 評価データ: {len(X_test)}行")

    # モデルの学習
    model = train_model(X_train, y_train)

    # モデルの評価
    evaluate_model(model, X_test, y_test)

    # モデルの保存
    save_model(model)

    return model


def run_predict_mode():
    """予測モードを実行する"""
    print("=== 予測モード実行 ===")

    # 学習済みモデルの読み込み
    model = load_model()

    # テストデータの読み込み
    test_data = load_data("data/test.csv")

    # 予測実行
    predictions = predict_results(model, test_data)

    # 予測結果の保存
    save_predictions(test_data, predictions)


def main():
    """メイン処理"""
    print("競艇勝敗予測プログラム開始")

    # コマンドライン引数の解析
    args = parse_arguments()

    if args.mode is None:
        # 引数なしの場合は学習→予測の順で実行
        print("学習・予測両方のモードを実行します")
        run_train_mode(args)
        run_predict_mode()
    elif args.mode == "train":
        run_train_mode(args)
    elif args.mode == "predict":
        run_predict_mode()

    print("プログラム実行完了")


if __name__ == "__main__":
    main()
