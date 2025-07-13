#!/usr/bin/env python3
"""
勝敗予測プログラム
ランダムフォレストを使用してボートレースの勝敗を予測します。
"""

import json
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


class RacerResultsPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoders = {}
        self.feature_columns = [
            "枠番",
            "選手登番",
            "年齢",
            "体重",
            "級別",
            "全国勝率",
            "モーター2連率",
            "ボート2連率",
        ]

    def load_data(self, file_path):
        """データを読み込み、日付列を追加"""
        print("データを読み込み中...")
        df = pd.read_csv(file_path)

        # 日付列を作成（年、月、日を結合）
        df["日付"] = pd.to_datetime(
            df["年"].astype(str)
            + "-"
            + df["月"].astype(str).str.zfill(2)
            + "-"
            + df["日"].astype(str).str.zfill(2)
        )

        print(f"読み込み完了: {len(df)}行のデータ")
        return df

    def preprocess_data(self, df, is_training=True):
        """データの前処理"""
        print("データの前処理中...")

        # 勝敗列が空でない行のみを使用
        df = df[df["勝敗"] != ""].copy()

        # エンコード前のデータを保存（戻り値用）
        df_before_encoding = df.copy()

        # 特徴量の欠損値処理
        for col in self.feature_columns:
            if col in df.columns:
                if df[col].dtype == "object":
                    # カテゴリカル変数の欠損値は最頻値で補完
                    mode_val = (
                        df[col].mode()[0] if not df[col].mode().empty else "Unknown"
                    )
                    df[col] = df[col].fillna(mode_val)
                    df_before_encoding[col] = df_before_encoding[col].fillna(mode_val)
                else:
                    # 数値変数の欠損値は平均値で補完
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)
                    df_before_encoding[col] = df_before_encoding[col].fillna(mean_val)

        # カテゴリカル変数のエンコーディング
        categorical_columns = ["級別"]
        for col in categorical_columns:
            if col in df.columns:
                if is_training:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                        df[col] = self.label_encoders[col].fit_transform(
                            df[col].astype(str)
                        )
                    else:
                        df[col] = self.label_encoders[col].transform(
                            df[col].astype(str)
                        )
                else:
                    # テスト時は学習済みエンコーダーを使用
                    if col in self.label_encoders:
                        df[col] = self.label_encoders[col].transform(
                            df[col].astype(str)
                        )

        # 勝敗を数値に変換
        df["勝敗"] = pd.to_numeric(df["勝敗"], errors="coerce")
        df_before_encoding["勝敗"] = pd.to_numeric(
            df_before_encoding["勝敗"], errors="coerce"
        )

        print(f"前処理完了: {len(df)}行のデータ")
        return df, df_before_encoding

    def split_data_by_date(self, df):
        """日付に基づいてデータを分割"""
        print("日付によるデータ分割中...")

        # 学習用: 2024年1月1日～2024年11月30日
        train_end_date = datetime(2024, 11, 30)
        train_data = df[df["日付"] <= train_end_date].copy()

        # 予測用: 2024年12月1日～2024年12月31日
        test_start_date = datetime(2024, 12, 1)
        test_end_date = datetime(2024, 12, 31)
        test_data = df[
            (df["日付"] >= test_start_date) & (df["日付"] <= test_end_date)
        ].copy()

        print(f"学習用データ: {len(train_data)}行")
        print(f"予測用データ: {len(test_data)}行")

        return train_data, test_data

    def prepare_features(self, df):
        """特徴量とターゲットを準備"""
        # 利用可能な特徴量のみを選択
        available_features = [col for col in self.feature_columns if col in df.columns]

        X = df[available_features].copy()
        y = df["勝敗"].copy()

        # 数値型に変換
        for col in available_features:
            X[col] = pd.to_numeric(X[col], errors="coerce")

        # 欠損値を平均値で補完
        X = X.fillna(X.mean())

        return X, y, available_features

    def train_model(self, X_train, y_train):
        """モデルを学習"""
        print("ランダムフォレストモデルを学習中...")

        # 欠損値を除去
        mask = ~(X_train.isnull().any(axis=1) | y_train.isnull())
        X_train_clean = X_train[mask]
        y_train_clean = y_train[mask]

        print(f"学習データ: {len(X_train_clean)}行")
        print(f"勝ち（1）: {sum(y_train_clean == 1)}件")
        print(f"負け（0）: {sum(y_train_clean == 0)}件")

        self.model.fit(X_train_clean, y_train_clean)
        print("学習完了")

        # 特徴量重要度を表示
        feature_importance = pd.DataFrame(
            {
                "feature": X_train_clean.columns,
                "importance": self.model.feature_importances_,
            }
        ).sort_values("importance", ascending=False)

        print("\n特徴量重要度:")
        for _, row in feature_importance.iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")

    def predict_and_evaluate(self, X_test, y_test, test_data_before_encoding):
        """予測と評価"""
        print("\n予測と評価を実行中...")

        # 欠損値を除去
        mask = ~(X_test.isnull().any(axis=1) | y_test.isnull())
        X_test_clean = X_test[mask]
        y_test_clean = y_test[mask]
        test_data_clean = test_data_before_encoding[mask].copy()

        print(f"テストデータ: {len(X_test_clean)}行")

        if len(X_test_clean) == 0:
            print("テストデータがありません")
            return None, None

        # 予測実行
        y_pred = self.model.predict(X_test_clean)

        # 予測結果をエンコード前データに追加
        test_data_clean["予測値"] = y_pred

        # 評価指標を計算
        accuracy = accuracy_score(y_test_clean, y_pred)
        precision = precision_score(y_test_clean, y_pred, zero_division=0)
        recall = recall_score(y_test_clean, y_pred, zero_division=0)
        f1 = f1_score(y_test_clean, y_pred, zero_division=0)

        results = {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
        }

        return results, test_data_clean

    def save_intermediate_data(
        self,
        train_data,
        test_data,
        train_data_before_encoding,
        test_data_before_encoding,
        X_train,
        X_test,
        y_train,
        y_test,
        test_data_with_predictions=None,
    ):
        """中間データをCSVファイルに保存"""
        print("\n中間データを保存中...")

        try:
            # 学習用データ（前処理済み）を保存
            train_output = train_data.copy()
            train_output.to_csv(
                "train_data_preprocessed.csv", index=False, encoding="utf-8-sig"
            )
            print(
                f"学習用前処理済みデータを保存: train_data_preprocessed.csv ({len(train_output)}行)"
            )

            # テスト用データ（前処理済み）を保存
            test_output = test_data.copy()
            test_output.to_csv(
                "test_data_preprocessed.csv", index=False, encoding="utf-8-sig"
            )
            print(
                f"テスト用前処理済みデータを保存: test_data_preprocessed.csv ({len(test_output)}行)"
            )

            # エンコード前のテストデータを保存
            test_before_encoding = test_data_before_encoding.copy()
            test_before_encoding.to_csv(
                "test_data_before_encoding.csv", index=False, encoding="utf-8-sig"
            )
            print(
                f"テスト用エンコード前データを保存: test_data_before_encoding.csv ({len(test_before_encoding)}行)"
            )

            # 学習用特徴量データを保存
            train_features = X_train.copy()
            train_features["勝敗"] = y_train
            train_features.to_csv(
                "train_features.csv", index=False, encoding="utf-8-sig"
            )
            print(
                f"学習用特徴量データを保存: train_features.csv ({len(train_features)}行)"
            )

            # テスト用特徴量データを保存
            test_features = X_test.copy()
            test_features["勝敗"] = y_test
            test_features.to_csv("test_features.csv", index=False, encoding="utf-8-sig")
            print(
                f"テスト用特徴量データを保存: test_features.csv ({len(test_features)}行)"
            )

            # 予測結果付きのテストデータを保存
            if test_data_with_predictions is not None:
                # 日付列を削除し、勝敗と予測値を先頭に移動
                output_data = test_data_with_predictions.copy()

                # 日付列を削除
                if "日付" in output_data.columns:
                    output_data = output_data.drop("日付", axis=1)

                # 勝敗と予測値を先頭に移動
                cols = output_data.columns.tolist()
                if "勝敗" in cols and "予測値" in cols:
                    # 勝敗と予測値を削除
                    cols.remove("勝敗")
                    cols.remove("予測値")
                    # 先頭に勝敗と予測値を追加
                    new_cols = ["勝敗", "予測値"] + cols
                    output_data = output_data[new_cols]

                output_data.to_csv(
                    "test_data_with_predictions.csv", index=False, encoding="utf-8-sig"
                )
                print(
                    f"予測結果付きテストデータを保存: test_data_with_predictions.csv ({len(output_data)}行)"
                )

        except Exception as e:
            print(f"中間データ保存中にエラーが発生: {e}")

    def run_prediction(self, file_path):
        """メイン処理を実行"""
        try:
            # データ読み込み
            df = self.load_data(file_path)

            # 前処理（学習用）
            df, df_before_encoding = self.preprocess_data(df, is_training=True)

            # 日付による分割
            train_data, test_data = self.split_data_by_date(df)
            train_data_before_encoding, test_data_before_encoding = (
                self.split_data_by_date(df_before_encoding)
            )

            if len(train_data) == 0:
                print("学習用データがありません")
                return None

            if len(test_data) == 0:
                print("テスト用データがありません")
                return None

            # 特徴量準備
            X_train, y_train, features = self.prepare_features(train_data)
            X_test, y_test, _ = self.prepare_features(test_data)

            print(f"\n使用する特徴量: {features}")

            # モデル学習
            self.train_model(X_train, y_train)

            # 予測と評価
            results, test_data_with_predictions = self.predict_and_evaluate(
                X_test, y_test, test_data_before_encoding
            )

            # 中間データを保存
            self.save_intermediate_data(
                train_data,
                test_data,
                train_data_before_encoding,
                test_data_before_encoding,
                X_train,
                X_test,
                y_train,
                y_test,
                test_data_with_predictions,
            )

            return results

        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return None


def main():
    """メイン関数"""
    predictor = RacerResultsPredictor()

    # 予測実行
    results = predictor.run_prediction("/app/data/racer_program.csv")

    if results:
        print("\n=== 予測結果 ===")
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("予測を実行できませんでした")


if __name__ == "__main__":
    main()
