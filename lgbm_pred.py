#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競艇予測 LightGBM 予測実行

このスクリプトでは、学習済みのLightGBMモデルを使用して競艇の1着予測を実行します。

データソース:
- data/pred.csv: 予測用特徴量データ
- model/lgbm_model.txt: 学習済みLightGBMモデル

目標:
- 学習済みモデルを読み込み
- 予測用データに対して1着確率を予測
- 予測結果の分析と可視化
"""

# 必要なライブラリをインポート
from datetime import datetime

import lightgbm as lgb
import matplotlib

# GUI環境がない場合に対応
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 日本語フォント設定
# plt.rcParams["font.family"] = "DejaVu Sans"
sns.set_style("whitegrid")
plt.style.use("default")

# 日本語フォント設定（エラー回避のため try-except で囲む）
try:
    matplotlib.rc("font", family="IPAexGothic")
except:
    print("Warning: IPAexGothic font not found, using default font")


def create_race_id(row):
    """レースIDを作成する関数"""
    date_str = f"{row['年']:04d}{row['月']:02d}{row['日']:02d}"
    place_str = f"{row['レース場番号']:02d}"
    race_str = f"{row['レース番号']:02d}"
    return int(f"{date_str}{place_str}{race_str}")


def load_model(model_path="model/lgbm_model.txt"):
    """
    学習済みLightGBMモデルを読み込む関数
    """
    print("=== 学習済みモデル読み込み ===")
    try:
        model = lgb.Booster(model_file=model_path)
        print("モデル読み込み成功!")
        print(f"特徴量数: {model.num_feature()}")
        print(f"学習ラウンド数: {model.num_trees()}")
        return model
    except FileNotFoundError:
        print(f"エラー: {model_path} が見つかりません")
        print("先にtrain_lgbm.ipynbでモデルを学習してください")
        raise


def load_prediction_data(file_path="data/pred.csv"):
    """
    予測用データを読み込み、基本情報を表示する関数
    """
    print("=== 予測用データ読み込み ===")
    try:
        pred_df = pd.read_csv(file_path)
        print(f"データ形状: {pred_df.shape}")
        print(f"カラム一覧: {pred_df.columns.tolist()}")

        # データの基本情報
        print(f"\n=== データ概要 ===")
        print(f"総レコード数: {len(pred_df)}")
        print(f"レース数: {len(pred_df) // 6} (想定)")
        print(f"欠損値: {pred_df.isnull().sum().sum()}")

        print("予測用データの先頭5行:")
        print(pred_df.head())
        return pred_df
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりません")
        print("先にcreate_features.py pred [日付]で予測用データを作成してください")
        raise


def make_predictions(model, pred_df):
    """
    LightGBMモデルを使用して予測を実行する関数
    """
    print("=== 予測実行 ===")
    predictions = model.predict(
        pred_df.drop(columns=["レースID"]), num_iteration=model.best_iteration
    )
    print("予測完了!")
    return predictions


def main():
    """メイン処理"""

    # 学習済みモデルの読み込み
    model = load_model()

    pred_df = load_prediction_data()

    # レース場番号（int）→場名のマッピング
    track_mapping = {
        1: "桐生",
        2: "戸田",
        3: "江戸川",
        4: "平和島",
        5: "多摩川",
        6: "浜名湖",
        7: "蒲郡",
        8: "常滑",
        9: "津",
        10: "三国",
        11: "びわこ",
        12: "住之江",
        13: "尼崎",
        14: "鳴門",
        15: "丸亀",
        16: "児島",
        17: "宮島",
        18: "徳山",
        19: "下関",
        20: "若松",
        21: "芦屋",
        22: "福岡",
        23: "唐津",
        24: "大村",
    }

    predictions = make_predictions(model, pred_df)

    # 予測結果データフレームを作成
    pred_results = pred_df.copy()

    # 番組表を読み込む
    try:
        programs_df = pd.read_csv("data/programs.csv")
        print("番組表読み込み完了!")
        print("番組表の先頭5行:")
        print(programs_df.head())
    except FileNotFoundError:
        print("エラー: data/programs.csv が見つかりません")  # noqa: E501
        raise

    programs_df["レースID"] = programs_df.apply(create_race_id, axis=1)
    print("番組表読み込み完了!")
    print("番組表の先頭5行:")
    print(programs_df.head())

    # レーサー情報を読み込む
    try:
        racers_df = pd.read_csv("data/racers.csv")
        print("レーサー情報読み込み完了!")
        print("レーサー情報の先頭5行:")
        print(racers_df.head())
    except FileNotFoundError:
        print("エラー: data/racers.csv が見つかりません")
        raise

    # レース場番号をレース場名に変換
    programs_df["レース場"] = programs_df["レース場番号"].map(track_mapping)

    # 予測結果に番組表の情報を追加
    print("=== 予測結果に番組表情報追加 ===")
    # 予測結果と番組表の結合キー
    keys = ["レースID", "枠番"]
    # pred_resultsとprograms_dfの重複カラム（["レースID", "枠番"]以外）を取得
    dup_cols = [
        col
        for col in programs_df.columns
        if col in pred_results.columns and col not in keys
    ]
    # 重複カラムをpred_resultsから削除
    pred_results = pred_results.drop(columns=dup_cols)

    # 番組表と予測結果を結合
    pred_results = pred_results.merge(programs_df, on=keys, how="left")
    print("予測結果と番組表の結合完了!")

    # 予測結果とレーサー情報の結合
    racers_df = racers_df.rename(columns={"登番": "選手登番"})
    # 同じ選手登番が複数ある場合は最新のデータ（末尾）のみを使用
    racers_df_unique = racers_df.drop_duplicates(subset=["選手登番"], keep="last")
    pred_results = pred_results.merge(
        racers_df_unique[["選手登番", "名前漢字"]], on="選手登番", how="left"
    )

    # 予測結果を追加
    pred_results["1着予測確率"] = predictions
    pred_results["予測順位"] = 0  # 初期化

    print(f"予測確率の統計:")
    print(f"最小値: {predictions.min():.4f}")
    print(f"最大値: {predictions.max():.4f}")
    print(f"平均値: {predictions.mean():.4f}")
    print(f"標準偏差: {predictions.std():.4f}")

    # 予測確率の分布を表示
    print("予測確率の統計情報:")
    print(f"分布の四分位数:")
    print(f"25%: {np.percentile(predictions, 25):.4f}")
    print(f"50%: {np.percentile(predictions, 50):.4f}")
    print(f"75%: {np.percentile(predictions, 75):.4f}")

    # グラフは保存のみ（表示しない）
    plt.figure(figsize=(10, 6))
    plt.hist(predictions, bins=50, alpha=0.7, edgecolor="black")
    plt.title("1着予測確率の分布")
    plt.xlabel("予測確率")
    plt.ylabel("頻度")
    plt.grid(True, alpha=0.3)
    plt.savefig("data/prediction_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()  # メモリ解放
    print("予測確率分布グラフを data/prediction_distribution.png に保存しました")

    # レース毎の予測順位を計算
    print("=== レース毎予測順位計算 ===")

    # 枠番をレースIDとして使用（簡易的にレースを識別）
    # 実際のレースIDがない場合は、6艇ずつグループ化
    race_groups = []
    for i in range(0, len(pred_results), 6):
        race_group = pred_results.iloc[i : i + 6].copy()
        if len(race_group) == 6:  # 6艇揃っている場合のみ処理
            # 予測確率の降順で順位付け
            race_group = race_group.sort_values("1着予測確率", ascending=False)
            race_group["予測順位"] = range(1, 7)
            race_groups.append(race_group)

    # 結果を統合
    if race_groups:
        final_results = pd.concat(race_groups, ignore_index=True)

        print(f"処理レース数: {len(race_groups)}")
        print(f"総艇数: {len(final_results)}")

        # 枠番別の予測順位分布
        print(f"\n=== 枠番別予測順位分布 ===")
        rank_by_frame = (
            final_results.groupby("枠番")["予測順位"]
            .value_counts()
            .unstack(fill_value=0)
        )
        print(rank_by_frame)

        # 枠番別の平均予測確率
        print(f"\n=== 枠番別平均予測確率 ===")
        prob_by_frame = (
            final_results.groupby("枠番")["1着予測確率"].agg(["mean", "std"]).round(4)
        )
        print(prob_by_frame)
    else:
        print("エラー: 6艇1組のレースデータが見つかりません")
        return

    # 枠番別予測分析の可視化
    if race_groups:
        plt.figure(figsize=(15, 10))

        # 枠番別平均予測確率
        plt.subplot(2, 3, 1)
        frame_prob = final_results.groupby("枠番")["1着予測確率"].mean()
        plt.bar(frame_prob.index, frame_prob.values)
        plt.title("枠番別平均1着予測確率")
        plt.xlabel("枠番")
        plt.ylabel("平均予測確率")
        plt.grid(True, alpha=0.3)

        # 枠番別1位予測率
        plt.subplot(2, 3, 2)
        rank1_rate = final_results.groupby("枠番")["予測順位"].apply(
            lambda x: (x == 1).mean()
        )
        plt.bar(rank1_rate.index, rank1_rate.values)
        plt.title("枠番別1位予測率")
        plt.xlabel("枠番")
        plt.ylabel("1位予測率")
        plt.grid(True, alpha=0.3)

        # 予測確率のボックスプロット
        plt.subplot(2, 3, 3)
        frame_data = [
            final_results[final_results["枠番"] == i]["1着予測確率"].values
            for i in range(1, 7)
        ]
        plt.boxplot(frame_data, labels=range(1, 7))
        plt.title("枠番別予測確率分布")
        plt.xlabel("枠番")
        plt.ylabel("予測確率")
        plt.grid(True, alpha=0.3)

        # 予測順位分布（ヒートマップ）
        plt.subplot(2, 3, 4)
        rank_dist = (
            final_results.groupby("枠番")["予測順位"]
            .value_counts()
            .unstack(fill_value=0)
        )
        rank_dist_pct = rank_dist.div(rank_dist.sum(axis=1), axis=0) * 100
        sns.heatmap(rank_dist_pct, annot=True, fmt=".1f", cmap="YlOrRd")
        plt.title("枠番別予測順位分布(%)")
        plt.xlabel("予測順位")
        plt.ylabel("枠番")

        # 高予測確率レースの分析
        plt.subplot(2, 3, 5)
        high_prob_races = []
        for race_group in race_groups:
            max_prob = race_group["1着予測確率"].max()
            high_prob_races.append(max_prob)

        plt.hist(high_prob_races, bins=20, alpha=0.7, edgecolor="black")
        plt.title("各レース最高予測確率の分布")
        plt.xlabel("最高予測確率")
        plt.ylabel("レース数")
        plt.grid(True, alpha=0.3)

        # 予測の信頼度分析
        plt.subplot(2, 3, 6)
        confidence_scores = []
        for race_group in race_groups:
            sorted_probs = race_group["1着予測確率"].sort_values(ascending=False)
            if len(sorted_probs) >= 2:
                confidence = sorted_probs.iloc[0] - sorted_probs.iloc[1]
                confidence_scores.append(confidence)

        plt.hist(confidence_scores, bins=20, alpha=0.7, edgecolor="black")
        plt.title("予測信頼度（1位-2位確率差）")
        plt.xlabel("確率差")
        plt.ylabel("レース数")
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig("data/prediction_analysis_charts.png", dpi=150, bbox_inches="tight")
        plt.close()  # メモリ解放
        print("分析チャートを data/prediction_analysis_charts.png に保存しました")

        print(f"\n=== 予測信頼度統計 ===")
        print(f"平均信頼度: {np.mean(confidence_scores):.4f}")
        print(
            f"高信頼度レース数 (差>0.1): {sum(1 for c in confidence_scores if c > 0.1)}"
        )
        print(
            f"低信頼度レース数 (差<0.05): {sum(1 for c in confidence_scores if c < 0.05)}"
        )

    # 予測結果のサンプル表示と保存
    if race_groups:
        print("=== 予測結果サンプル（上位5レース） ===")

        # 各レースの最高予測確率でソート
        race_max_probs = []
        for i, race_group in enumerate(race_groups[:5]):  # 最初の5レースを表示
            max_prob = race_group["1着予測確率"].max()
            max_frame = race_group.loc[race_group["1着予測確率"].idxmax(), "枠番"]
            race_max_probs.append((i + 1, max_prob, max_frame, race_group))

        # 最高予測確率でソート
        race_max_probs.sort(key=lambda x: x[1], reverse=True)

        for race_num, max_prob, max_frame, race_group in race_max_probs:
            print(
                f"\n--- レース{race_num} (最高確率: {max_prob:.3f}, 予想1位: {max_frame}枠) ---"
            )
            display_cols = [
                "レースID",
                "枠番",
                "級別",
                "レース内全国勝率差",
                "レース内コース別1着率差",
                "レース内コース別複勝率差",
                "1着予測確率",
                "予測順位",
            ]
            # カラムが存在するもののみを選択
            available_cols = [col for col in display_cols if col in race_group.columns]
            race_display = race_group[available_cols].sort_values("予測順位")
            for _, row in race_display.iterrows():
                print(
                    f"{row['枠番']}枠: 確率{row['1着予測確率']:.3f} (順位{row['予測順位']}) "
                    f"級別{row['級別']} 全国勝率差{row['レース内全国勝率差']:.3f} コース別1着率差{row['レース内コース別1着率差']:.3f} コース別複勝率差{row['レース内コース別複勝率差']:.3f}"
                )

        output_columns = [
            "年",
            "月",
            "日",
            "レース場",
            "レース番号",
            "枠番",
            "級別",
            "名前漢字",
            "年齢",
            "支部",
            "体重",
            "全国勝率",
            "全国2連率",
            "当地勝率",
            "当地2連率",
            "モーター番号",
            "モーター2連率",
            "ボート番号",
            "ボート2連率",
            # "レース内全国勝率差",
            # "レース内コース別1着率差",
            # "レース内コース別複勝率差",
            "1着予測確率",
            "予測順位",
        ]

        # 予測結果を必要なカラムのみを選択して保存CSVファイルに保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/predictions_{timestamp}.csv"
        final_results.reindex(columns=output_columns).to_csv(
            output_file, index=False, encoding="utf-8-sig"
        )

        print(f"\n=== 予測結果保存 ===")
        print(f"ファイル名: {output_file}")
        print(f"レコード数: {len(final_results)}")
        print(f"レース数: {len(race_groups)}")

        # 簡易的な買い目提案
        print(f"\n=== 買い目提案（参考） ===")
        high_confidence_races = [
            (i + 1, race_group)
            for i, race_group in enumerate(race_groups)
            if race_group["1着予測確率"].max() > 0.3  # 30%以上の確率
        ]

        if high_confidence_races:
            print(f"高信頼度レース数: {len(high_confidence_races)}")
            for race_num, race_group in high_confidence_races[:3]:  # 上位3レース
                top_frame = race_group.loc[race_group["1着予測確率"].idxmax(), "枠番"]
                top_prob = race_group["1着予測確率"].max()
                print(f"レース{race_num}: {top_frame}枠単勝 (確率{top_prob:.1%})")
        else:
            print("高信頼度レースはありません（最高確率<30%）")
    else:
        print("予測結果がありません")


if __name__ == "__main__":
    main()
