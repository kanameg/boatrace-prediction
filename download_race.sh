#!/bin/bash
# -*- coding: utf-8 -*-
#
# 競走成績・番組表ダウンロードスクリプト
# 指定されたタイプ（競走成績または番組表）のデータをダウンロード、解凍、文字コード変換を行う
#
# 使用方法: ./download_race.sh [p|r] YYYY-MM-DD
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
    echo "使用方法: $0 [p|r] YYYY-MM-DD"
    echo "  p: 番組表をダウンロード"
    echo "  r: 競走成績をダウンロード"
    echo "  YYYY-MM-DD: 日付（例: 2025-07-13 または 2025-7-13）"
    exit 1
}

# 引数チェック
if [ $# -ne 2 ]; then
    echo "エラー: 引数が不足しています。"
    show_usage
fi

TYPE=$1
DATE_ARG=$2

# タイプの妥当性チェック
if [[ "$TYPE" != "p" && "$TYPE" != "r" ]]; then
    error_exit "タイプは 'p'（番組表）または 'r'（競走成績）を指定してください: $TYPE"
fi

# 日付形式のチェック（YYYY-MM-DD または YYYY-M-D）
if ! [[ "$DATE_ARG" =~ ^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$ ]]; then
    error_exit "日付はYYYY-MM-DD形式で入力してください（0埋めなしも可）: $DATE_ARG"
fi

# 日付を分割
YEAR=$(echo $DATE_ARG | cut -d'-' -f1)
MONTH=$(echo $DATE_ARG | cut -d'-' -f2)
DAY=$(echo $DATE_ARG | cut -d'-' -f3)

# 日付の妥当性チェック
if ! date -d "$DATE_ARG" > /dev/null 2>&1; then
    error_exit "無効な日付です: $DATE_ARG"
fi

# 数値変換（先頭の0を除去）
MONTH=$((10#$MONTH))
DAY=$((10#$DAY))

# フォーマット調整（0埋め）
YEAR_FULL=$(printf "%04d" $YEAR)
YEAR_SHORT=$(printf "%02d" $((YEAR % 100)))
MONTH_PADDED=$(printf "%02d" $MONTH)
DAY_PADDED=$(printf "%02d" $DAY)

# タイプに応じた設定
if [ "$TYPE" = "p" ]; then
    # 番組表の設定
    TYPE_NAME="番組表"
    PREFIX="b"
    URL_PATH="B"
    OUTPUT_DIR="data/raw/programs"
else
    # 競走成績の設定
    TYPE_NAME="競走成績"
    PREFIX="k"
    URL_PATH="K"
    OUTPUT_DIR="data/raw/results"
fi

# ディレクトリ作成
mkdir -p "$OUTPUT_DIR"

# ファイル名とURL生成
ARCHIVE_FILENAME="${PREFIX}${YEAR_SHORT}${MONTH_PADDED}${DAY_PADDED}.lzh"
RESULT_FILENAME="${PREFIX}${YEAR_SHORT}${MONTH_PADDED}${DAY_PADDED}.txt"
UTF8_FILENAME="${PREFIX}${YEAR_SHORT}${MONTH_PADDED}${DAY_PADDED}_u8.txt"

DOWNLOAD_URL="https://www1.mbrace.or.jp/od2/${URL_PATH}/${YEAR_FULL}${MONTH_PADDED}/${ARCHIVE_FILENAME}"
ARCHIVE_PATH="${ARCHIVE_FILENAME}"  # カレントディレクトリに一時保存
RESULT_PATH="${OUTPUT_DIR}/${UTF8_FILENAME}"

echo "処理開始: ${DATE_ARG}の${TYPE_NAME}データを処理します"
echo "ダウンロードURL: ${DOWNLOAD_URL}"

# 既にファイルが存在する場合はスキップ
if [ -f "$RESULT_PATH" ]; then
    echo "ファイルが既に存在します: $RESULT_PATH"
    echo "処理をスキップします。"
    exit 0
fi

# ダウンロード処理（wgetコマンドを使用して、指定されたURLからlzh形式の圧縮ファイルをダウンロード）
# ダウンロードしたファイルは、カレントディレクトリに一時的に保存される（後ほど削除）
echo "ダウンロード中: ${ARCHIVE_FILENAME}"
if ! wget -q --show-progress -O "$ARCHIVE_PATH" "$DOWNLOAD_URL"; then
    error_exit "ダウンロードに失敗しました: $DOWNLOAD_URL"
fi

echo "ダウンロード完了: $ARCHIVE_PATH"

# 解凍処理（lhaコマンドを使用して解凍。解凍後、ファイルはカレントディレクトリに一時保存）
echo "解凍中: ${ARCHIVE_FILENAME}"
if ! lha x "$ARCHIVE_PATH" > /dev/null 2>&1; then
    error_exit "解凍に失敗しました: $ARCHIVE_PATH"
fi

# 解凍されたファイルの存在確認
if [ ! -f "$RESULT_FILENAME" ]; then
    error_exit "解凍後のファイルが見つかりません: $RESULT_FILENAME"
fi

echo "解凍完了: $RESULT_FILENAME"

# 正常に解凍された場合、元のアーカイブファイルは削除
if [ -f "$ARCHIVE_PATH" ]; then
    rm "$ARCHIVE_PATH"
    echo "アーカイブファイルを削除しました: $ARCHIVE_PATH"
fi

# 文字コード変換（Shift-JIS → UTF-8）
# 解凍されたファイルはShift-JISエンコーディングで保存されているため、iconvコマンドを使用してUTF-8に変換
# 変換後のファイルは番組表と競走結果でそれぞれ指定のディレクトリに保存
echo "文字コード変換中: Shift-JIS → UTF-8"
if ! iconv -f SHIFT_JIS -t UTF-8 "$RESULT_FILENAME" > "$RESULT_PATH"; then
    error_exit "文字コード変換に失敗しました: $RESULT_FILENAME"
fi

echo "文字コード変換完了: $RESULT_PATH"

# 一時ファイルの削除（正常に変換された場合、元のShift-JISファイルは削除）
if [ -f "$RESULT_FILENAME" ]; then
    rm "$RESULT_FILENAME"
    echo "Shift-JISファイルを削除しました: $RESULT_FILENAME"
fi

echo "処理完了: ${DATE_ARG}の${TYPE_NAME}データ処理が正常に完了しました"
echo "出力ファイル: $RESULT_PATH"
