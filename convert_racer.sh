#!/bin/bash
# -*- coding: utf-8 -*-
#
# レーサー期別成績変換スクリプト
# 指定された期（前期、後期）の成績データをCSV形式に変換する
#
# 使用方法: ./convert_racer_record.sh [e|l] YYYY
#

# エラー処理を有効にする
set -e

# 関数: エラーメッセージを表示して終了
error_exit() {
    echo "エラー: $1" >&2
    exit 1
}

# 関数: 使用方法を表示
show_usage() {
    echo "使用方法: $0 [e|l] YYYY"
    echo "  e: 前期データを変換"
    echo "  l: 後期データを変換"
    echo "  YYYY: 年4桁（例: 2025）"
    exit 1
}

# 引数チェック
if [ $# -ne 2 ]; then
    echo "エラー: 引数が不足しています。"
    show_usage
fi

PERIOD=$1
YEAR=$2

# 期の妥当性チェック
if [[ "$PERIOD" != "e" && "$PERIOD" != "l" ]]; then
    error_exit "期は 'e'（前期）または 'l'（後期）を指定してください: $PERIOD"
fi

# 引数の妥当性チェック
if ! [[ "$YEAR" =~ ^[0-9]{4}$ ]]; then
    error_exit "年は4桁の数値で入力してください: $YEAR"
fi

# フォーマット調整（0埋め）
YEAR_FULL=$(printf "%04d" $YEAR)

# 期名の設定
if [ "$PERIOD" = "e" ]; then
    PERIOD_NAME="前期"
else
    PERIOD_NAME="後期"
fi

# ファイル名とパス生成
INPUT_FILENAME="racer_${YEAR_FULL}${PERIOD}.txt"
INPUT_PATH="data/raw/racer/${INPUT_FILENAME}"
OUTPUT_PATH="data/racer.csv"

echo "処理開始: ${YEAR_FULL}年${PERIOD_NAME}のレーサー期別成績データを変換します"
echo "入力ファイル: ${INPUT_PATH}"
echo "出力ファイル: ${OUTPUT_PATH} (統一ファイルに追記)"

# 入力ファイルの存在確認
if [ ! -f "$INPUT_PATH" ]; then
    error_exit "入力ファイルが見つかりません: $INPUT_PATH"
fi

# 出力ディレクトリの作成
mkdir -p "data"

# Pythonスクリプトを実行してデータ変換
echo "データ変換中..."
if ! python3 convert_racer.py "$PERIOD" "$YEAR"; then
    error_exit "データ変換に失敗しました"
fi

echo "変換完了: ${YEAR_FULL}年${PERIOD_NAME}のレーサー期別成績データ変換が正常に完了しました"
echo "出力ファイル: $OUTPUT_PATH"

# 出力ファイルの確認
if [ -f "$OUTPUT_PATH" ]; then
    echo "統一CSVファイルに正常に追記されました"
    echo "総レコード数: $(tail -n +2 "$OUTPUT_PATH" | wc -l) 件"
else
    error_exit "出力ファイルが作成されませんでした"
fi
