#!/bin/bash

# Programs CSV増分インポートスクリプト
# data/programs.csvをSQLite3データベースに増分インポートする
# 既存データとの重複をチェックして新しいデータのみを追加
# 新しい構造: 1艇1行のフォーマットに対応

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="${SCRIPT_DIR}/../data/programs.csv"
DB_FILE="${SCRIPT_DIR}/boat_race.db"
SQL_FILE="${SCRIPT_DIR}/programs.sql"

echo "=== Programs CSV増分インポート開始 ==="

# CSVファイルの存在確認
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: $CSV_FILE が見つかりません"
    exit 1
fi

# データベースファイルの存在確認
if [ ! -f "$DB_FILE" ]; then
    echo "エラー: データベースファイルが見つかりません: $DB_FILE"
    echo "まず import_programs.sh を実行してテーブルを作成してください"
    exit 1
fi

echo "CSVファイル: $CSV_FILE"
echo "データベース: $DB_FILE"
echo "SQLファイル: $SQL_FILE"

# CSVの行数を確認
CSV_LINES=$(wc -l < "$CSV_FILE")
echo "CSVファイル行数: $CSV_LINES 行（ヘッダー含む）"

# テーブル存在チェック
TABLE_EXISTS=$(sqlite3 "$DB_FILE" "SELECT name FROM sqlite_master WHERE type='table' AND name='programs';" 2>/dev/null)
if [ -z "$TABLE_EXISTS" ]; then
    echo ""
    echo "programsテーブルが存在しません。テーブルを作成中..."
    if [ ! -f "$SQL_FILE" ]; then
        echo "エラー: $SQL_FILE が見つかりません"
        exit 1
    fi
    sqlite3 "$DB_FILE" < "$SQL_FILE"
    echo "テーブル作成完了"
fi

# インポート前のレコード数確認
BEFORE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
echo ""
echo "インポート前のレコード数: $BEFORE_COUNT"

# CSVデータを増分インポート
echo ""
echo "CSVデータを増分インポート中..."
sqlite3 "$DB_FILE" <<EOF
-- 一時テーブル作成
DROP TABLE IF EXISTS temp_programs;
CREATE TABLE temp_programs (
  年 TEXT,
  月 TEXT,
  日 TEXT,
  レース場番号 TEXT,
  レース番号 TEXT,
  距離 TEXT,
  投票締切時間 TEXT,
  枠番 TEXT,
  選手登番 TEXT,
  年齢 TEXT,
  支部 TEXT,
  体重 TEXT,
  級別 TEXT,
  全国勝率 TEXT,
  全国2連率 TEXT,
  当地勝率 TEXT,
  当地2連率 TEXT,
  モーター番号 TEXT,
  モーター2連率 TEXT,
  ボート番号 TEXT,
  ボート2連率 TEXT
);

.mode csv
.headers off
.import $CSV_FILE temp_programs

-- 既存データと重複しないデータのみを挿入（年月日、会場、レース番号、選手登番の組み合わせでチェック）
INSERT INTO programs (
  year, month, day, venue_code, race_number, distance_m, deadline_time,
  frame_number, racer_number, age, branch, weight, class,
  national_win_rate, national_quinella_rate, local_win_rate, local_quinella_rate,
  motor_number, motor_quinella_rate, boat_number, boat_quinella_rate
)
SELECT 
SELECT 
  CASE WHEN 年 = '' OR 年 IS NULL THEN NULL ELSE CAST(年 AS INTEGER) END,
  CASE WHEN 月 = '' OR 月 IS NULL THEN NULL ELSE CAST(月 AS INTEGER) END,
  CASE WHEN 日 = '' OR 日 IS NULL THEN NULL ELSE CAST(日 AS INTEGER) END,
  CASE WHEN レース場番号 = '' OR レース場番号 IS NULL THEN NULL ELSE CAST(レース場番号 AS INTEGER) END,
  CASE WHEN レース番号 = '' OR レース番号 IS NULL THEN NULL ELSE CAST(レース番号 AS INTEGER) END,
  CASE WHEN 距離 = '' OR 距離 IS NULL THEN NULL ELSE CAST(距離 AS INTEGER) END,
  投票締切時間,
  CASE WHEN 枠番 = '' OR 枠番 IS NULL THEN NULL ELSE CAST(枠番 AS INTEGER) END,
  CASE WHEN 選手登番 = '' OR 選手登番 IS NULL THEN NULL ELSE CAST(選手登番 AS INTEGER) END,
  CASE WHEN 年齢 = '' OR 年齢 IS NULL THEN NULL ELSE CAST(年齢 AS INTEGER) END,
  支部,
  CASE WHEN 体重 = '' OR 体重 IS NULL THEN NULL ELSE CAST(体重 AS REAL) END,
  級別,
  CASE WHEN 全国勝率 = '' OR 全国勝率 IS NULL THEN NULL ELSE CAST(全国勝率 AS REAL) END,
  CASE WHEN 全国2連率 = '' OR 全国2連率 IS NULL THEN NULL ELSE CAST(全国2連率 AS REAL) END,
  CASE WHEN 当地勝率 = '' OR 当地勝率 IS NULL THEN NULL ELSE CAST(当地勝率 AS REAL) END,
  CASE WHEN 当地2連率 = '' OR 当地2連率 IS NULL THEN NULL ELSE CAST(当地2連率 AS REAL) END,
  CASE WHEN モーター番号 = '' OR モーター番号 IS NULL THEN NULL ELSE CAST(モーター番号 AS INTEGER) END,
  CASE WHEN モーター2連率 = '' OR モーター2連率 IS NULL THEN NULL ELSE CAST(モーター2連率 AS REAL) END,
  CASE WHEN ボート番号 = '' OR ボート番号 IS NULL THEN NULL ELSE CAST(ボート番号 AS INTEGER) END,
  CASE WHEN ボート2連率 = '' OR ボート2連率 IS NULL THEN NULL ELSE CAST(ボート2連率 AS REAL) END
FROM temp_programs
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != ''
  AND NOT EXISTS (
    SELECT 1 FROM programs 
    WHERE programs.year = CAST(temp_programs.年 AS INTEGER) 
      AND programs.month = CAST(temp_programs.月 AS INTEGER)
      AND programs.day = CAST(temp_programs.日 AS INTEGER)
      AND programs.venue_code = CAST(temp_programs.レース場番号 AS INTEGER)
      AND programs.race_number = CAST(temp_programs.レース番号 AS INTEGER)
      AND programs.racer_number = CAST(temp_programs.選手登番 AS INTEGER)
  );

-- 一時テーブルを削除
DROP TABLE temp_programs;
EOF

if [ $? -ne 0 ]; then
    echo "エラー: CSVインポートに失敗しました"
    exit 1
fi

# インポート後のレコード数確認
AFTER_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
NEW_RECORDS=$((AFTER_COUNT - BEFORE_COUNT))

echo ""
echo "インポート結果確認..."
echo "インポート後のレコード数: $AFTER_COUNT"
echo "新規追加レコード数: $NEW_RECORDS"

# 新しく追加されたデータの期間確認（新規レコードがある場合）
if [ $NEW_RECORDS -gt 0 ]; then
    # データ期間の確認
    PERIOD_INFO=$(sqlite3 "$DB_FILE" "
    SELECT 
      MIN(year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) as start_date,
      MAX(year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) as end_date,
      COUNT(DISTINCT year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) as total_days
    FROM programs;")
    
    echo "データ期間: $PERIOD_INFO"
    
    # 最新データのサンプル表示
    echo ""
    echo "最新データサンプル:"
    sqlite3 "$DB_FILE" "
    SELECT 
      year || '-' || printf('%02d', month) || '-' || printf('%02d', day) as date,
      venue_code as venue,
      race_number as race,
      frame_number as frame,
      racer_number,
      age,
      class
    FROM programs 
    ORDER BY year DESC, month DESC, day DESC, venue_code DESC, race_number DESC, frame_number ASC
    LIMIT 3;"
else
    echo "新規データはありませんでした。"
fi

echo ""
echo "=== Programs CSV増分インポート完了 ==="
