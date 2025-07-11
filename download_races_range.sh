#!/bin/bash
# -*- coding: utf-8 -*-
#
# 範囲指定ダウンロードスクリプト
# このスクリプトは、指定された期間の競争成績と番組表を一括でダウンロードします。
# 期間は開始日と終了日で指定します。
# ダウンロードには、download_race.shスクリプトを使用します。
#
# 使用方法: ./download_races_range.sh [p|r] START_YYYY START_MM START_DD END_YYYY END_MM END_DD
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
    echo "使用方法: $0 [p|r] START_YYYY START_MM START_DD END_YYYY END_MM END_DD"
    echo "  p: 番組表をダウンロード"
    echo "  r: 競走成績をダウンロード"
    echo "  START_YYYY: 開始年4桁（例: 2025）"
    echo "  START_MM: 開始月1桁または2桁（例: 7 または 07）"
    echo "  START_DD: 開始日1桁または2桁（例: 1 または 01）"
    echo "  END_YYYY: 終了年4桁（例: 2025）"
    echo "  END_MM: 終了月1桁または2桁（例: 7 または 07）"
    echo "  END_DD: 終了日1桁または2桁（例: 9 または 09）"
    echo ""
    echo "例: $0 r 2025 7 1 2025 7 9  # 2025年7月1日から9日まで競走成績をダウンロード"
    echo "例: $0 p 2025 7 1 2025 7 9  # 2025年7月1日から9日まで番組表をダウンロード"
    exit 1
}

# 関数: 日付を検証
validate_date() {
    local year=$1
    local month=$2
    local day=$3
    local label=$4
    
    if ! [[ "$year" =~ ^[0-9]{4}$ ]]; then
        error_exit "${label}年は4桁の数値で入力してください: $year"
    fi
    
    if ! [[ "$month" =~ ^[0-9]{1,2}$ ]] || [ "$month" -lt 1 ] || [ "$month" -gt 12 ]; then
        error_exit "${label}月は1〜12の範囲で入力してください: $month"
    fi
    
    if ! [[ "$day" =~ ^[0-9]{1,2}$ ]] || [ "$day" -lt 1 ] || [ "$day" -gt 31 ]; then
        error_exit "${label}日は1〜31の範囲で入力してください: $day"
    fi
}

# 関数: 日付をエポック秒に変換
date_to_epoch() {
    local year=$1
    local month=$2
    local day=$3
    
    date -d "${year}-${month}-${day}" +%s 2>/dev/null || error_exit "無効な日付です: ${year}-${month}-${day}"
}

# 関数: エポック秒を次の日に進める
next_day() {
    local epoch=$1
    echo $((epoch + 86400))  # 86400秒 = 24時間
}

# 関数: エポック秒を年月日に変換
epoch_to_date() {
    local epoch=$1
    date -d "@${epoch}" "+%Y %m %d"
}

# download_race.shの存在確認
if [ ! -f "./download_race.sh" ]; then
    error_exit "download_race.sh が見つかりません。同じディレクトリに配置してください。"
fi

if [ ! -x "./download_race.sh" ]; then
    error_exit "download_race.sh に実行権限がありません。chmod +x download_race.sh を実行してください。"
fi

# 引数チェック
if [ $# -ne 7 ]; then
    echo "エラー: 引数が不足しています。"
    show_usage
fi

TYPE=$1
START_YEAR=$2
START_MONTH=$3
START_DAY=$4
END_YEAR=$5
END_MONTH=$6
END_DAY=$7

# タイプの妥当性チェック
if [[ "$TYPE" != "p" && "$TYPE" != "r" ]]; then
    error_exit "タイプは 'p'（番組表）または 'r'（競走成績）を指定してください: $TYPE"
fi

# タイプ名の設定
if [ "$TYPE" = "p" ]; then
    TYPE_NAME="番組表"
else
    TYPE_NAME="競走成績"
fi

# 引数の妥当性チェック
validate_date "$START_YEAR" "$START_MONTH" "$START_DAY" "開始"
validate_date "$END_YEAR" "$END_MONTH" "$END_DAY" "終了"

# 日付の前後関係チェック
START_EPOCH=$(date_to_epoch "$START_YEAR" "$START_MONTH" "$START_DAY")
END_EPOCH=$(date_to_epoch "$END_YEAR" "$END_MONTH" "$END_DAY")

if [ "$START_EPOCH" -gt "$END_EPOCH" ]; then
    error_exit "開始日が終了日より後になっています: ${START_YEAR}-${START_MONTH}-${START_DAY} > ${END_YEAR}-${END_MONTH}-${END_DAY}"
fi

echo "複数${TYPE_NAME}ダウンロード開始"
echo "期間: ${START_YEAR}年${START_MONTH}月${START_DAY}日 〜 ${END_YEAR}年${END_MONTH}月${END_DAY}日"

# 処理する日数を計算
TOTAL_DAYS=$(( (END_EPOCH - START_EPOCH) / 86400 + 1 ))
echo "処理対象: ${TOTAL_DAYS}日間"
echo ""

# カウンター
SUCCESS_COUNT=0
ERROR_COUNT=0
CURRENT_DAY=1

# 各日付に対してダウンロード処理を実行
# ダウンロードは、サーバーに負荷をかけないように、1日ごとに行い、ダウンロードの間隔は1秒とする
CURRENT_EPOCH=$START_EPOCH
while [ "$CURRENT_EPOCH" -le "$END_EPOCH" ]; do
    # エポック秒を年月日に変換
    DATE_INFO=($(epoch_to_date $CURRENT_EPOCH))
    YEAR=${DATE_INFO[0]}
    MONTH=$((10#${DATE_INFO[1]}))  # 先頭の0を除去
    DAY=$((10#${DATE_INFO[2]}))    # 先頭の0を除去
    
    echo "[${CURRENT_DAY}/${TOTAL_DAYS}] ${YEAR}年${MONTH}月${DAY}日の処理中..."
    
    # download_race.shを実行
    if ./download_race.sh "$TYPE" "$YEAR" "$MONTH" "$DAY"; then
        echo "  → 成功"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  → エラー: ${YEAR}年${MONTH}月${DAY}日のダウンロードに失敗しました"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        error_exit "各日付のダウンロードに失敗しました: ${YEAR}年${MONTH}月${DAY}日"
    fi
    
    # 次の日に進む
    CURRENT_EPOCH=$(next_day $CURRENT_EPOCH)
    CURRENT_DAY=$((CURRENT_DAY + 1))
    
    # サーバー負荷軽減のため1秒待機（最後の日以外）
    if [ "$CURRENT_EPOCH" -le "$END_EPOCH" ]; then
        echo "  1秒待機中..."
        sleep 1
    fi
    
    echo ""
done

echo "複数${TYPE_NAME}ダウンロード完了"
echo "============================================"
echo "処理結果:"
echo "  成功: ${SUCCESS_COUNT}日"
echo "  エラー: ${ERROR_COUNT}日"
echo "  合計: ${TOTAL_DAYS}日"
echo "============================================"

if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "警告: ${ERROR_COUNT}日分のダウンロードでエラーが発生しました。"
    exit 1
else
    echo "全ての処理が正常に完了しました。"
    exit 0
fi
