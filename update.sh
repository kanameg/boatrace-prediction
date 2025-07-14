#!/bin/bash
# -*- coding: utf-8 -*-

# 競艇予測処理の流れに従って実行するスクリプト
# 使用方法: ./update.sh 2025-07-13

set -e  # エラーが発生した場合にスクリプトを終了

# 引数チェック
if [ $# -ne 1 ]; then
    echo "使用方法: $0 YYYY-MM-DD"
    echo "例: $0 2025-07-13"
    exit 1
fi

# 変換の開始日を指定
START_DATE=2025-01-01  # CSVデータの開始日として2025年1月1日を指定

# 日付の解析
TARGET_DATE=$1
YEAR=$(echo $TARGET_DATE | cut -d'-' -f1)
MONTH=$(echo $TARGET_DATE | cut -d'-' -f2)
DAY=$(echo $TARGET_DATE | cut -d'-' -f3)

# 対象日のepoch秒を取得
TARGET_EPOCH=$(date -d "$TARGET_DATE" +%s)

# 翌日のepoch秒を計算（24時間 = 86400秒を足す）
NEXT_EPOCH=$((TARGET_EPOCH + 86400))

# 翌日の日付を取得
NEXT_DATE=$(date -d "@$NEXT_EPOCH" +%Y-%m-%d)
NEXT_YEAR=$(date -d "@$NEXT_EPOCH" +%Y)
NEXT_MONTH=$(date -d "@$NEXT_EPOCH" +%m)
NEXT_DAY=$(date -d "@$NEXT_EPOCH" +%d)

# ゼロパディング（既に正しい形式だが念のため）
MONTH=$(printf "%02d" $((10#$MONTH)))
DAY=$(printf "%02d" $((10#$DAY)))

echo "========================================="
echo "競艇予測処理開始"
echo "本日: $TARGET_DATE"
echo "翌日: $NEXT_DATE"
echo "========================================="

# 1. 本日までの競走結果データを取得
echo "1. 本日までの競走結果データを取得中..."
./download_race.sh r $TARGET_DATE

# 2. 翌日の番組表データを取得
echo "2. 翌日の番組表データを取得中..."
./download_race.sh p $NEXT_DATE

# 3. 本日までの競走結果データを変換
echo "3. 本日までの競走結果データを変換中..."
./convert_results.sh $START_DATE $TARGET_DATE

# 4. 翌日の番組表データを変換
echo "4. 翌日の番組表データを変換中..."
./convert_programs.sh $START_DATE $NEXT_DATE

# # 5. 1選手1行の形式に変換
# echo "5. レース番組データを1選手1行形式に変換中..."
# python convert_race_programs.py

# # 6. トレーニング用データを作成
# echo "6. トレーニング用データを作成中..."
# python generate_tt_data.py train 2025 1 1 $YEAR $MONTH $DAY

# # 7. 予測用データを作成
# echo "7. 予測用データを作成中..."
# python generate_tt_data.py test $NEXT_YEAR $NEXT_MONTH $NEXT_DAY

# # 8. LightGBMモデルで学習・評価を実行
# echo "8. LightGBMモデルで学習・評価を実行中..."
# TRAIN_END_DATE="$YEAR-$MONTH-$DAY"
# # 本日の日付を評価日として使用
# python racer_lgbm_predictor.py train 2025-01-01 $TRAIN_END_DATE $TRAIN_END_DATE

# # 9. LightGBMモデルで予測を実行
# echo "9. LightGBMモデルで予測を実行中..."
# python racer_lgbm_predictor.py predict $NEXT_DATE

# # 10. RandomForestモデルでも予測を実行（比較用）
# echo "10. RandomForestモデルで予測を実行中..."
# python racer_randomf_predictor.py predict $NEXT_DATE

echo "========================================="
echo "競艇予測処理完了"
echo "予測対象日: $NEXT_DATE"
echo "結果ファイル:"
echo "  - predict_results.csv (予測結果)"
echo "  - evaluation_results.csv (評価結果)"
echo "========================================="

