#!/bin/bash
# -*- coding: utf-8 -*-
#
# 範囲指定競走結果データ変換スクリプト
# 指定された期間の競走結果データを一括で変換します。
# 期間は開始日と終了日で指定します。
# 期間内の各日の競走結果データをconvert_result.pyスクリプトを使用して変換します。
#
# 使用方法: ./convert_results.sh START_DATE END_DATE
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
    echo "使用方法: $0 START_DATE END_DATE"
    echo "  START_DATE: 開始日（YYYY-MM-DD形式、例: 2025-07-01 または 2025-7-1）"
    echo "  END_DATE: 終了日（YYYY-MM-DD形式、例: 2025-07-09 または 2025-7-9）"
    echo ""
    echo "例: $0 2025-07-01 2025-07-09  # 2025年7月1日から9日まで競走結果データを変換"
    exit 1
}

# 関数: 日付を検証
validate_date() {
    local date_str=$1
    local label=$2
    
    # 日付形式のチェック（YYYY-MM-DD または YYYY-M-D）
    if ! [[ "$date_str" =~ ^[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}$ ]]; then
        error_exit "${label}日付はYYYY-MM-DD形式で入力してください（0埋めなしも可）: $date_str"
    fi
    
    # 日付の妥当性チェック
    if ! date -d "$date_str" > /dev/null 2>&1; then
        error_exit "無効な${label}日付です: $date_str"
    fi
}

# 関数: 日付をエポック秒に変換
date_to_epoch() {
    local date_str=$1
    
    date -d "$date_str" +%s 2>/dev/null || error_exit "無効な日付です: $date_str"
}

# 関数: エポック秒を次の日に進める
next_day() {
    local epoch=$1
    echo $((epoch + 86400))  # 86400秒 = 24時間
}

# convert_result.pyの存在確認
if [ ! -f "./convert_result.py" ]; then
    error_exit "convert_result.py が見つかりません。同じディレクトリに配置してください。"
fi

# 引数チェック
if [ $# -ne 2 ]; then
    echo "エラー: 引数が不足しています。"
    show_usage
fi

START_DATE=$1
END_DATE=$2

# 引数の妥当性チェック
validate_date "$START_DATE" "開始"
validate_date "$END_DATE" "終了"

# 日付の前後関係チェック
START_EPOCH=$(date_to_epoch "$START_DATE")
END_EPOCH=$(date_to_epoch "$END_DATE")

if [ "$START_EPOCH" -gt "$END_EPOCH" ]; then
    error_exit "開始日が終了日より後になっています: $START_DATE > $END_DATE"
fi

echo "競走結果データ一括変換開始"
echo "期間: $START_DATE 〜 $END_DATE"

# 既存の出力ファイルを削除（毎回作り直すため）
OUTPUT_FILE="data/results.csv"
if [ -f "$OUTPUT_FILE" ]; then
    echo "既存のファイルを削除します: $OUTPUT_FILE"
    rm "$OUTPUT_FILE"
fi

# 処理する日数を計算
TOTAL_DAYS=$(( (END_EPOCH - START_EPOCH) / 86400 + 1 ))
echo "処理対象: ${TOTAL_DAYS}日間"
echo ""

# カウンター
SUCCESS_COUNT=0
ERROR_COUNT=0
CURRENT_DAY=1

# 各日付に対して競走結果データ変換処理を実行
CURRENT_EPOCH=$START_EPOCH
while [ "$CURRENT_EPOCH" -le "$END_EPOCH" ]; do
    # エポック秒を日付文字列に変換
    CURRENT_DATE=$(date -d "@$CURRENT_EPOCH" +%Y-%m-%d)

    # 5行戻す（エスケープシーケンス）
    printf '\033[5A'
    # 進捗表示
    echo "[${CURRENT_DAY}/${TOTAL_DAYS}] $CURRENT_DATE の処理中..."

    # convert_result.pyを実行（YYYY-MM-DD形式で渡す）
    if python convert_result.py "$CURRENT_DATE"; then
        echo "  → 成功"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  → エラー: $CURRENT_DATE の変換に失敗しました"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        error_exit "各日付の変換に失敗しました: $CURRENT_DATE"
    fi

    # 次の日に進む
    CURRENT_EPOCH=$(next_day $CURRENT_EPOCH)
    CURRENT_DAY=$((CURRENT_DAY + 1))

    echo ""
done

echo "競走結果データ一括変換完了"
echo "============================================"
echo "処理結果:"
echo "  成功: ${SUCCESS_COUNT}日"
echo "  エラー: ${ERROR_COUNT}日"
echo "  合計: ${TOTAL_DAYS}日"
echo "============================================"

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "警告: ${ERROR_COUNT}日分の変換でエラーが発生しました。"
    exit 1
else
    echo "全ての処理が正常に完了しました。"
    echo "出力ファイル: data/results.csv"
    exit 0
fi
