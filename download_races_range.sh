#!/bin/bash
# -*- coding: utf-8 -*-
#
# 範囲指定ダウンロードスクリプト
# このスクリプトは、指定された期間の競争成績と番組表を一括でダウンロードします。
# 期間は開始日と終了日で指定します。
# ダウンロードには、download_race.shスクリプトを使用します。
#
# 使用方法: ./download_races_range.sh [p|r] START_DATE END_DATE
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
    echo "使用方法: $0 [p|r] START_DATE END_DATE"
    echo "  p: 番組表をダウンロード"
    echo "  r: 競走成績をダウンロード"
    echo "  START_DATE: 開始日（YYYY-MM-DD形式、例: 2025-07-01 または 2025-7-1）"
    echo "  END_DATE: 終了日（YYYY-MM-DD形式、例: 2025-07-09 または 2025-7-9）"
    echo ""
    echo "例: $0 r 2025-07-01 2025-07-09  # 2025年7月1日から9日まで競走成績をダウンロード"
    echo "例: $0 p 2025-7-1 2025-7-9      # 2025年7月1日から9日まで番組表をダウンロード"
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

# download_race.shの存在確認
if [ ! -f "./download_race.sh" ]; then
    error_exit "download_race.sh が見つかりません。同じディレクトリに配置してください。"
fi

if [ ! -x "./download_race.sh" ]; then
    error_exit "download_race.sh に実行権限がありません。chmod +x download_race.sh を実行してください。"
fi

# 引数チェック
if [ $# -ne 3 ]; then
    echo "エラー: 引数が不足しています。"
    show_usage
fi

TYPE=$1
START_DATE=$2
END_DATE=$3

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
validate_date "$START_DATE" "開始"
validate_date "$END_DATE" "終了"

# 日付の前後関係チェック
START_EPOCH=$(date_to_epoch "$START_DATE")
END_EPOCH=$(date_to_epoch "$END_DATE")

if [ "$START_EPOCH" -gt "$END_EPOCH" ]; then
    error_exit "開始日が終了日より後になっています: $START_DATE > $END_DATE"
fi

echo "複数${TYPE_NAME}ダウンロード開始"
echo "期間: $START_DATE 〜 $END_DATE"

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
    # エポック秒を日付文字列に変換
    CURRENT_DATE=$(date -d "@$CURRENT_EPOCH" +%Y-%m-%d)
    
    echo "[${CURRENT_DAY}/${TOTAL_DAYS}] $CURRENT_DATE の処理中..."
    
    # download_race.shを実行して出力をキャプチャ（YYYY-MM-DD形式で渡す）
    DOWNLOAD_OUTPUT=$(./download_race.sh "$TYPE" "$CURRENT_DATE" 2>&1)
    DOWNLOAD_RESULT=$?
    
    if [ $DOWNLOAD_RESULT -eq 0 ]; then
        # 出力内容でスキップかどうかを判定
        if echo "$DOWNLOAD_OUTPUT" | grep -q "処理をスキップします"; then
            echo "  → スキップ（ファイル既存）"
            SHOULD_SLEEP=false
        else
            echo "  → 成功"
            SHOULD_SLEEP=true
        fi
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  → エラー: $CURRENT_DATE のダウンロードに失敗しました"
        echo "$DOWNLOAD_OUTPUT"
        ERROR_COUNT=$((ERROR_COUNT + 1))
        error_exit "各日付のダウンロードに失敗しました: $CURRENT_DATE"
    fi
    
    # 次の日に進む
    CURRENT_EPOCH=$(next_day $CURRENT_EPOCH)
    CURRENT_DAY=$((CURRENT_DAY + 1))
    
    # サーバー負荷軽減のため1秒待機（最後の日以外、かつスキップでない場合のみ）
    if [ "$CURRENT_EPOCH" -le "$END_EPOCH" ] && [ "$SHOULD_SLEEP" = true ]; then
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
