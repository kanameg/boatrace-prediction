#!/bin/bash

# Programs CSV一括インポートスクリプト
# data/programs.csvをSQLite3データベースにインポートする
# 新しい構造: 1艇1行のフォーマットに対応

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="${SCRIPT_DIR}/../data/programs.csv"
DB_FILE="${SCRIPT_DIR}/boat_race.db"
SQL_FILE="${SCRIPT_DIR}/programs.sql"

echo "=== Programs CSV一括インポート開始 ==="

# CSVファイルの存在確認
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: $CSV_FILE が見つかりません"
    exit 1
fi

# SQLファイルの存在確認
if [ ! -f "$SQL_FILE" ]; then
    echo "エラー: $SQL_FILE が見つかりません"
    exit 1
fi

echo "CSVファイル: $CSV_FILE"
echo "データベース: $DB_FILE"
echo "SQLファイル: $SQL_FILE"

# CSVの行数を確認
CSV_LINES=$(wc -l < "$CSV_FILE")
echo "CSVファイル行数: $CSV_LINES 行（ヘッダー含む）"

# テーブル作成
echo ""
echo "テーブルを作成中..."
sqlite3 "$DB_FILE" < "$SQL_FILE"
echo "テーブル作成完了"

# CSVデータをインポート
echo ""
echo "CSVデータをインポート中..."

sqlite3 "$DB_FILE" <<EOF
.mode csv
.headers on
.import '$CSV_FILE' temp_programs

-- temp_programsから本テーブルにデータを変換・挿入
INSERT INTO programs (
  year, month, day, venue_code, race_number, distance_m, deadline_time,
  frame_number, racer_number, age, branch, weight, class,
  national_win_rate, national_quinella_rate, local_win_rate, local_quinella_rate,
  motor_number, motor_quinella_rate, boat_number, boat_quinella_rate
)
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
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != '';

-- 一時テーブル削除
DROP TABLE temp_programs;
EOF

# インポート結果の確認
echo ""
echo "インポート結果確認..."

IMPORTED_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
echo "インポート件数: $IMPORTED_COUNT 件"

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

echo ""
echo "=== Programs CSV一括インポート完了 ==="
