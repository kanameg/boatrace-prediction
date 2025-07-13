#!/bin/bash
# -*- coding: utf-8 -*-
#
# レーサー期別成績ダウンロードスクリプト
# 指定された期（前期、後期）の成績データをダウンロード、解凍、文字コード変換を行う
#
# 使用方法: ./download_racer_record.sh [e|l] YYYY
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
    echo "  e: 前期データをダウンロード"
    echo "  l: 後期データをダウンロード"
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

# 期に応じた設定
if [ "$PERIOD" = "e" ]; then
    # 前期の設定（2025年前期の場合は2024年10月までの成績で決まるため）
    PERIOD_NAME="前期"
    PREV_YEAR=$((YEAR - 1))
    PREV_YEAR_2DIGIT=$(printf "%02d" $((PREV_YEAR % 100)))
    ARCHIVE_FILENAME="fan${PREV_YEAR_2DIGIT}10.lzh"
else
    # 後期の設定（2025年後期の場合は2025年4月までの成績で決まるため）
    PERIOD_NAME="後期"
    YEAR_2DIGIT=$(printf "%02d" $((YEAR % 100)))
    ARCHIVE_FILENAME="fan${YEAR_2DIGIT}04.lzh"
fi

# ディレクトリ作成
OUTPUT_DIR="data/raw/racer_records"
mkdir -p "$OUTPUT_DIR"

# ファイル名とURL生成
DOWNLOAD_URL="https://www.boatrace.jp/static_extra/pc_static/download/data/kibetsu/${ARCHIVE_FILENAME}"
ARCHIVE_PATH="${ARCHIVE_FILENAME}"  # カレントディレクトリに一時保存
EXTRACTED_FILENAME="${ARCHIVE_FILENAME%.lzh}.txt"  # 解凍後のファイル名（アーカイブ名から.lzhを除去して.txtを追加）
UTF8_FILENAME="racer_${YEAR_FULL}${PERIOD}.txt"
RESULT_PATH="${OUTPUT_DIR}/${UTF8_FILENAME}"

echo "処理開始: ${YEAR_FULL}年${PERIOD_NAME}のレーサー期別成績データを処理します"
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
if [ ! -f "$EXTRACTED_FILENAME" ]; then
    error_exit "解凍後のファイルが見つかりません: $EXTRACTED_FILENAME"
fi

echo "解凍完了: $EXTRACTED_FILENAME"

# 正常に解凍された場合、元のアーカイブファイルは削除
if [ -f "$ARCHIVE_PATH" ]; then
    rm "$ARCHIVE_PATH"
    echo "アーカイブファイルを削除しました: $ARCHIVE_PATH"
fi

# 文字コード変換（Shift-JIS → UTF-8）
# 解凍されたファイルはShift-JISエンコーディングで保存されているため、iconvコマンドを使用してUTF-8に変換
# 変換後のファイルは指定のディレクトリに保存
echo "文字コード変換中: Shift-JIS → UTF-8"
if ! iconv -f SHIFT_JIS -t UTF-8 "$EXTRACTED_FILENAME" > "$RESULT_PATH"; then
    error_exit "文字コード変換に失敗しました: $EXTRACTED_FILENAME"
fi

echo "文字コード変換完了: $RESULT_PATH"

# 一時ファイルの削除（正常に変換された場合、元のShift-JISファイルは削除）
if [ -f "$EXTRACTED_FILENAME" ]; then
    rm "$EXTRACTED_FILENAME"
    echo "Shift-JISファイルを削除しました: $EXTRACTED_FILENAME"
fi

echo "処理完了: ${YEAR_FULL}年${PERIOD_NAME}のレーサー期別成績データ処理が正常に完了しました"
echo "出力ファイル: $RESULT_PATH"
