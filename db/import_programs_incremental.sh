#!/bin/bash

# 番組表データ増分インポートスクリプト
# data/programs.csvから新規データのみをSQLite3データベースに追加する

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="${SCRIPT_DIR}/../data/programs.csv"
DB_FILE="${SCRIPT_DIR}/boat_race.db"

echo "=== 番組表データ増分インポート開始 ==="

# CSVファイルの存在確認
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: $CSV_FILE が見つかりません"
    exit 1
fi

# データベースファイルの存在確認
if [ ! -f "$DB_FILE" ]; then
    echo "エラー: データベース $DB_FILE が見つかりません"
    echo "先に import_programs.sh を実行してください"
    exit 1
fi

echo "CSVファイル: $CSV_FILE"
echo "データベース: $DB_FILE"

# CSVの行数を確認
CSV_LINES=$(wc -l < "$CSV_FILE")
echo "CSVファイル行数: $CSV_LINES 行（ヘッダー含む）"

# 現在のデータベース件数を確認
CURRENT_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
echo "現在のDB件数: $CURRENT_COUNT 件"

# 増分インポート実行
echo ""
echo "増分インポートを実行中..."

sqlite3 "$DB_FILE" <<EOF
-- 一時テーブル作成
DROP TABLE IF EXISTS temp_programs_incremental;
CREATE TABLE temp_programs_incremental (
  年 INTEGER,
  月 INTEGER,
  日 INTEGER,
  レース場番号 INTEGER,
  レース番号 INTEGER,
  選手登番 INTEGER,
  艇番 INTEGER,
  モーター番号 INTEGER,
  全国勝率 REAL,
  モーター勝率 REAL
);

-- CSVファイルをインポート
.mode csv
.headers on
.import '$CSV_FILE' temp_programs_incremental

-- 新規データのみを抽出して本テーブルに挿入
INSERT OR IGNORE INTO programs (
  year, month, day, venue_code, race_number,
  racer_number, boat_number, motor_number, boat_win_rate, motor_win_rate
)
SELECT
  年, 月, 日, レース場番号, レース番号,
  選手登番, 艇番, モーター番号, 全国勝率, モーター勝率
FROM temp_programs_incremental
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != ''
AND NOT EXISTS (
  SELECT 1 FROM programs p
  WHERE p.year = temp_programs_incremental.年
    AND p.month = temp_programs_incremental.月
    AND p.day = temp_programs_incremental.日
    AND p.venue_code = temp_programs_incremental.レース場番号
    AND p.race_number = temp_programs_incremental.レース番号
    AND p.racer_number = temp_programs_incremental.選手登番
);

-- 一時テーブル削除
DROP TABLE temp_programs_incremental;
EOF

# 増分インポート結果の確認
NEW_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
ADDED_COUNT=$((NEW_COUNT - CURRENT_COUNT))

echo ""
echo "増分インポート結果:"
echo "追加前: $CURRENT_COUNT 件"
echo "追加後: $NEW_COUNT 件"
echo "新規追加: $ADDED_COUNT 件"

# 最新データの確認
echo ""
echo "最新データ（3件）:"
sqlite3 "$DB_FILE" "
SELECT
  year || '-' || printf('%02d', month) || '-' || printf('%02d', day) as date,
  venue_code as venue,
  race_number as race,
  racer_number,
  boat_number
FROM programs
ORDER BY year DESC, month DESC, day DESC, venue_code DESC, race_number DESC
LIMIT 3;"

echo ""
echo "=== 番組表データ増分インポート完了 ==="
