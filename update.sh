#!/bin/bash
# -*- coding: utf-8 -*-

# データを最新にダウンロード・更新するスクリプト
# 使用方法: ./update.sh 2025-07-13

set -e  # エラーが発生した場合にスクリプトを終了

# 引数チェック
if [ $# -ne 1 ]; then
    echo "使用方法: $0 YYYY-MM-DD"
    echo "例: $0 2025-07-13"
    exit 1
fi

# 日付の解析
TARGET_DATE=$1

# 対象日のepoch秒を取得
TARGET_EPOCH=$(date -d "$TARGET_DATE" +%s)

# 翌日のepoch秒を計算（24時間 = 86400秒を足す）
NEXT_EPOCH=$((TARGET_EPOCH + 86400))

# 翌日の日付を取得
NEXT_DATE=$(date -d "@$NEXT_EPOCH" +%Y-%m-%d)

echo "========================================="
echo "競艇予測処理開始"
echo "本日: $TARGET_DATE"
echo "翌日: $NEXT_DATE"
echo "========================================="

# 1. 本日までの競走結果データを取得
echo ""
echo "----------------------------------------------------"
echo "1. 本日までの競走結果データを取得中..."
./download_race.sh r $TARGET_DATE

# 2. 翌日の番組表データを取得
echo ""
echo "----------------------------------------------------"
echo "2. 翌日の番組表データを取得中..."
./download_race.sh p $NEXT_DATE

echo "========================================="
echo "データ更新処理完了"
echo "========================================="
