#!/bin/bash

# レース結果データ増分インポートスクリプト
# data/results.csvから新規データのみをSQLite3データベースに追加する

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="${SCRIPT_DIR}/../data/results.csv"
DB_FILE="${SCRIPT_DIR}/boat_race.db"
SQL_FILE="${SCRIPT_DIR}/results.sql"

echo "=== レース結果データ増分インポート開始 ==="

# ファイルの存在確認
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: $CSV_FILE が見つかりません"
    exit 1
fi
if [ ! -f "$DB_FILE" ]; then
    echo "エラー: データベース $DB_FILE が見つかりません"
    echo "先に import_results.sh を実行してください"
    exit 1
fi
if [ ! -f "$SQL_FILE" ]; then
    echo "エラー: SQLスキーマファイル $SQL_FILE が見つかりません"
    exit 1
fi

echo "CSVファイル: $CSV_FILE"
echo "データベース: $DB_FILE"

# CSVの行数を確認
CSV_LINES=$(wc -l < "$CSV_FILE")
echo "CSVファイル行数: $CSV_LINES 行（ヘッダー含む）"

# 現在のデータベース件数を確認
CURRENT_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM results;")
echo "現在のDB件数: $CURRENT_COUNT 件"

# 増分インポート実行
echo ""
echo "増分インポートを実行中..."

sqlite3 "$DB_FILE" <<EOF
-- 一時テーブル作成
DROP TABLE IF EXISTS temp_results_incremental;
CREATE TABLE temp_results_incremental (
  年 INTEGER, 月 INTEGER, 日 INTEGER, レース場番号 INTEGER, レース番号 INTEGER,
  距離 INTEGER, 天候 TEXT, 風向 TEXT, 風速 REAL, 波高 REAL,
  単勝_艇番 TEXT, 単勝_払戻金 TEXT,
  複勝1着_艇番 TEXT, 複勝1着_払戻金 TEXT, 複勝2着_艇番 TEXT, 複勝2着_払戻金 TEXT,
  "2連単_艇番" TEXT, "2連単_払戻金" TEXT, "2連単_人気" TEXT,
  "2連複_艇番" TEXT, "2連複_払戻金" TEXT, "2連複_人気" TEXT,
  拡連複1_艇番 TEXT, 拡連複1_払戻金 TEXT, 拡連複1_人気 TEXT,
  拡連複2_艇番 TEXT, 拡連複2_払戻金 TEXT, 拡連複2_人気 TEXT,
  拡連複3_艇番 TEXT, 拡連複3_払戻金 TEXT, 拡連複3_人気 TEXT,
  "3連単_艇番" TEXT, "3連単_払戻金" TEXT, "3連単_人気" TEXT,
  "3連複_艇番" TEXT, "3連複_払戻金" TEXT, "3連複_人気" TEXT,
  着順 TEXT, 選手登番 TEXT, 艇番 TEXT, モーター番号 TEXT, ボート番号 TEXT,
  展示 TEXT, 進入 TEXT, スタートタイミング TEXT, レースタイム TEXT
);

-- CSVファイルをインポート
.mode csv
.headers on
.import '$CSV_FILE' temp_results_incremental

-- 新規データのみを抽出して本テーブルに挿入
INSERT OR IGNORE INTO results (
    year, month, day, venue_code, race_number, distance, weather, wind_direction, wind_speed, wave_height,
    win_boat_number, win_payout,
    place_1st_boat_number, place_1st_payout, place_2nd_boat_number, place_2nd_payout,
    exacta_boat_numbers, exacta_payout, exacta_popularity,
    quinella_boat_numbers, quinella_payout, quinella_popularity,
    wide_1_boat_numbers, wide_1_payout, wide_1_popularity,
    wide_2_boat_numbers, wide_2_payout, wide_2_popularity,
    wide_3_boat_numbers, wide_3_payout, wide_3_popularity,
    trifecta_boat_numbers, trifecta_payout, trifecta_popularity,
    trio_boat_numbers, trio_payout, trio_popularity,
    rank, racer_number, boat_number, motor_number, boat_data_number,
    exhibition_time, entry_course, start_timing, race_time
)
SELECT
    CAST(年 AS INTEGER), CAST(月 AS INTEGER), CAST(日 AS INTEGER), CAST(レース場番号 AS INTEGER), CAST(レース番号 AS INTEGER),
    CAST(距離 AS INTEGER), 天候, 風向, CAST(風速 AS REAL), CAST(波高 AS REAL),
    単勝_艇番, CAST(単勝_払戻金 AS INTEGER),
    複勝1着_艇番, CAST(複勝1着_払戻金 AS INTEGER), 複勝2着_艇番, CAST(複勝2着_払戻金 AS INTEGER),
    "2連単_艇番", CAST("2連単_払戻金" AS INTEGER), CAST("2連単_人気" AS INTEGER),
    "2連複_艇番", CAST("2連複_払戻金" AS INTEGER), CAST("2連複_人気" AS INTEGER),
    拡連複1_艇番, CAST(拡連複1_払戻金 AS INTEGER), CAST(拡連複1_人気 AS INTEGER),
    拡連複2_艇番, CAST(拡連複2_払戻金 AS INTEGER), CAST(拡連複2_人気 AS INTEGER),
    拡連複3_艇番, CAST(拡連複3_払戻金 AS INTEGER), CAST(拡連複3_人気 AS INTEGER),
    "3連単_艇番", CAST("3連単_払戻金" AS INTEGER), CAST("3連単_人気" AS INTEGER),
    "3連複_艇番", CAST("3連複_払戻金" AS INTEGER), CAST("3連複_人気" AS INTEGER),
    CAST(着順 AS INTEGER), CAST(選手登番 AS INTEGER), CAST(艇番 AS INTEGER), CAST(モーター番号 AS INTEGER), CAST(ボート番号 AS INTEGER),
    CAST(展示 AS REAL), CAST(進入 AS INTEGER), CAST(スタートタイミング AS REAL), レースタイム
FROM temp_results_incremental
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != ''
  AND NOT EXISTS (
    SELECT 1 FROM results r
    WHERE r.year = CAST(temp_results_incremental.年 AS INTEGER)
      AND r.month = CAST(temp_results_incremental.月 AS INTEGER)
      AND r.day = CAST(temp_results_incremental.日 AS INTEGER)
      AND r.venue_code = CAST(temp_results_incremental.レース場番号 AS INTEGER)
      AND r.race_number = CAST(temp_results_incremental.レース番号 AS INTEGER)
      AND r.boat_number = CAST(temp_results_incremental.艇番 AS INTEGER)
  );

-- 一時テーブル削除
DROP TABLE temp_results_incremental;
EOF

# 増分インポート結果の確認
NEW_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM results;")
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
  year, month, day, venue_code, race_number, boat_number, rank, racer_number
FROM results 
ORDER BY year DESC, month DESC, day DESC, venue_code DESC, race_number DESC, boat_number DESC
LIMIT 3;"

echo ""
echo "=== レース結果データ増分インポート完了 ==="
