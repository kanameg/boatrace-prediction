#!/bin/bash
# -*- coding: utf-8 -*-
#
# レース結果ダウンロードスクリプト
# 指定された日付のボートレース結果データをダウンロード、解凍、文字コード変換を行う
#
# 使用方法: ./download_result.sh YYYY MM DD
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
    echo "使用方法: $0 YYYY MM DD"
    echo "  YYYY: 年4桁（例: 2025）"
    echo "  MM: 1桁または2桁の月（例: 7 または 07）"
    echo "  DD: 1桁または2桁の日（例: 9 または 09）"
    exit 1
}

# 引数チェック
if [ $# -ne 3 ]; then
    echo "エラー: 引数が不足しています。"
    show_usage
fi

YEAR=$1
MONTH=$2
DAY=$3

# 引数の妥当性チェック
if ! [[ "$YEAR" =~ ^[0-9]{4}$ ]]; then
    error_exit "年は4桁の数値で入力してください: $YEAR"
fi

if ! [[ "$MONTH" =~ ^[0-9]{1,2}$ ]] || [ "$MONTH" -lt 1 ] || [ "$MONTH" -gt 12 ]; then
    error_exit "月は1〜12の範囲で入力してください: $MONTH"
fi

if ! [[ "$DAY" =~ ^[0-9]{1,2}$ ]] || [ "$DAY" -lt 1 ] || [ "$DAY" -gt 31 ]; then
    error_exit "日は1〜31の範囲で入力してください: $DAY"
fi

# フォーマット調整（0埋め）
YEAR_FULL=$(printf "%04d" $YEAR)
YEAR_SHORT=$(printf "%02d" $((YEAR % 100)))
MONTH_PADDED=$(printf "%02d" $MONTH)
DAY_PADDED=$(printf "%02d" $DAY)

# ディレクトリ作成
mkdir -p data/raw/archives
mkdir -p data/raw/results

# ファイル名とURL生成
ARCHIVE_FILENAME="k${YEAR_SHORT}${MONTH_PADDED}${DAY_PADDED}.lzh"
RESULT_FILENAME="k${YEAR_SHORT}${MONTH_PADDED}${DAY_PADDED}.txt"
UTF8_FILENAME="k${YEAR_SHORT}${MONTH_PADDED}${DAY_PADDED}_u8.txt"

DOWNLOAD_URL="https://www1.mbrace.or.jp/od2/K/${YEAR_FULL}${MONTH_PADDED}/${ARCHIVE_FILENAME}"
ARCHIVE_PATH="data/raw/archives/${ARCHIVE_FILENAME}"
RESULT_PATH="data/raw/results/${UTF8_FILENAME}"

echo "処理開始: ${YEAR_FULL}年${MONTH}月${DAY}日のデータを処理します"
echo "ダウンロードURL: ${DOWNLOAD_URL}"

# 既にファイルが存在する場合はスキップ
if [ -f "$RESULT_PATH" ]; then
    echo "ファイルが既に存在します: $RESULT_PATH"
    echo "処理をスキップします。"
    exit 0
fi

# ダウンロード処理
echo "ダウンロード中: ${ARCHIVE_FILENAME}"
if ! wget -q --show-progress -O "$ARCHIVE_PATH" "$DOWNLOAD_URL"; then
    error_exit "ダウンロードに失敗しました: $DOWNLOAD_URL"
fi

echo "ダウンロード完了: $ARCHIVE_PATH"

# 解凍処理
echo "解凍中: ${ARCHIVE_FILENAME}"
if ! lha x "$ARCHIVE_PATH" > /dev/null 2>&1; then
    error_exit "解凍に失敗しました: $ARCHIVE_PATH"
fi

# 解凍されたファイルの存在確認
if [ ! -f "$RESULT_FILENAME" ]; then
    error_exit "解凍後のファイルが見つかりません: $RESULT_FILENAME"
fi

echo "解凍完了: $RESULT_FILENAME"

# 文字コード変換（Shift-JIS → UTF-8）
echo "文字コード変換中: Shift-JIS → UTF-8"
if ! iconv -f SHIFT_JIS -t UTF-8 "$RESULT_FILENAME" > "$RESULT_PATH"; then
    error_exit "文字コード変換に失敗しました: $RESULT_FILENAME"
fi

echo "文字コード変換完了: $RESULT_PATH"

# 一時ファイルの削除
if [ -f "$RESULT_FILENAME" ]; then
    rm "$RESULT_FILENAME"
    echo "一時ファイルを削除しました: $RESULT_FILENAME"
fi

echo "処理完了: ${YEAR_FULL}年${MONTH}月${DAY}日のデータ処理が正常に完了しました"
echo "出力ファイル: $RESULT_PATH"
