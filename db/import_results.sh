#!/bin/bash

# レース結果データ一括インポートスクリプト
# data/results.csvをSQLite3データベースにインポートする

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="${SCRIPT_DIR}/../data/results.csv"
DB_FILE="${SCRIPT_DIR}/boat_race.db"
SQL_FILE="${SCRIPT_DIR}/results.sql"

echo "=== レース結果データ一括インポート開始 ==="

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
.import '$CSV_FILE' temp_results

-- temp_resultsから本テーブルにデータを変換・挿入
INSERT INTO results (
  year, month, day, venue_code, race_number,
  distance, weather, wind_direction, wind_speed, wave_height,
  win_boat_number, win_payout,
  place_1st_boat_number, place_1st_payout,
  place_2nd_boat_number, place_2nd_payout,
  exacta_boat_numbers, exacta_payout, exacta_popularity,
  quinella_boat_numbers, quinella_payout, quinella_popularity,
  wide_1_boat_numbers, wide_1_payout, wide_1_popularity,
  wide_2_boat_numbers, wide_2_payout, wide_2_popularity,
  wide_3_boat_numbers, wide_3_payout, wide_3_popularity,
  trifecta_boat_numbers, trifecta_payout, trifecta_popularity,
  trio_boat_numbers, trio_payout, trio_popularity,
  finish_position, racer_number, boat_number, motor_number, boat_number_assigned,
  exhibition_time, start_course, start_timing, race_time
)
SELECT 
  年, 月, 日, レース場番号, レース番号,
  距離, 天候, 風向, 風速, 波高,
  
  -- 払戻金情報の変換
  CASE WHEN 単勝_艇番 = '' OR 単勝_艇番 IS NULL THEN NULL ELSE 単勝_艇番 END,
  CASE WHEN 単勝_払戻金 = '' OR 単勝_払戻金 IS NULL THEN NULL ELSE CAST(単勝_払戻金 AS INTEGER) END,
  
  CASE WHEN 複勝1着_艇番 = '' OR 複勝1着_艇番 IS NULL THEN NULL ELSE 複勝1着_艇番 END,
  CASE WHEN 複勝1着_払戻金 = '' OR 複勝1着_払戻金 IS NULL THEN NULL ELSE CAST(複勝1着_払戻金 AS INTEGER) END,
  
  CASE WHEN 複勝2着_艇番 = '' OR 複勝2着_艇番 IS NULL THEN NULL ELSE 複勝2着_艇番 END,
  CASE WHEN 複勝2着_払戻金 = '' OR 複勝2着_払戻金 IS NULL THEN NULL ELSE CAST(複勝2着_払戻金 AS INTEGER) END,
  
  -- 2連単
  CASE WHEN [2連単_艇番] = '' OR [2連単_艇番] IS NULL THEN NULL ELSE [2連単_艇番] END,
  CASE WHEN [2連単_払戻金] = '' OR [2連単_払戻金] IS NULL THEN NULL ELSE CAST([2連単_払戻金] AS INTEGER) END,
  CASE WHEN [2連単_人気] = '' OR [2連単_人気] IS NULL THEN NULL ELSE CAST([2連単_人気] AS INTEGER) END,
  
  -- 2連複
  CASE WHEN [2連複_艇番] = '' OR [2連複_艇番] IS NULL THEN NULL ELSE [2連複_艇番] END,
  CASE WHEN [2連複_払戻金] = '' OR [2連複_払戻金] IS NULL THEN NULL ELSE CAST([2連複_払戻金] AS INTEGER) END,
  CASE WHEN [2連複_人気] = '' OR [2連複_人気] IS NULL THEN NULL ELSE CAST([2連複_人気] AS INTEGER) END,
  
  -- 拡連複
  CASE WHEN 拡連複1_艇番 = '' OR 拡連複1_艇番 IS NULL THEN NULL ELSE 拡連複1_艇番 END,
  CASE WHEN 拡連複1_払戻金 = '' OR 拡連複1_払戻金 IS NULL THEN NULL ELSE CAST(拡連複1_払戻金 AS INTEGER) END,
  CASE WHEN 拡連複1_人気 = '' OR 拡連複1_人気 IS NULL THEN NULL ELSE CAST(拡連複1_人気 AS INTEGER) END,
  
  CASE WHEN 拡連複2_艇番 = '' OR 拡連複2_艇番 IS NULL THEN NULL ELSE 拡連複2_艇番 END,
  CASE WHEN 拡連複2_払戻金 = '' OR 拡連複2_払戻金 IS NULL THEN NULL ELSE CAST(拡連複2_払戻金 AS INTEGER) END,
  CASE WHEN 拡連複2_人気 = '' OR 拡連複2_人気 IS NULL THEN NULL ELSE CAST(拡連複2_人気 AS INTEGER) END,
  
  CASE WHEN 拡連複3_艇番 = '' OR 拡連複3_艇番 IS NULL THEN NULL ELSE 拡連複3_艇番 END,
  CASE WHEN 拡連複3_払戻金 = '' OR 拡連複3_払戻金 IS NULL THEN NULL ELSE CAST(拡連複3_払戻金 AS INTEGER) END,
  CASE WHEN 拡連複3_人気 = '' OR 拡連複3_人気 IS NULL THEN NULL ELSE CAST(拡連複3_人気 AS INTEGER) END,
  
  -- 3連単
  CASE WHEN [3連単_艇番] = '' OR [3連単_艇番] IS NULL THEN NULL ELSE [3連単_艇番] END,
  CASE WHEN [3連単_払戻金] = '' OR [3連単_払戻金] IS NULL THEN NULL ELSE CAST([3連単_払戻金] AS INTEGER) END,
  CASE WHEN [3連単_人気] = '' OR [3連単_人気] IS NULL THEN NULL ELSE CAST([3連単_人気] AS INTEGER) END,
  
  -- 3連複
  CASE WHEN [3連複_艇番] = '' OR [3連複_艇番] IS NULL THEN NULL ELSE [3連複_艇番] END,
  CASE WHEN [3連複_払戻金] = '' OR [3連複_払戻金] IS NULL THEN NULL ELSE CAST([3連複_払戻金] AS INTEGER) END,
  CASE WHEN [3連複_人気] = '' OR [3連複_人気] IS NULL THEN NULL ELSE CAST([3連複_人気] AS INTEGER) END,
  
  -- 個別艇情報
  CASE WHEN 着順 = '' OR 着順 IS NULL THEN NULL ELSE CAST(着順 AS INTEGER) END,
  CASE WHEN 選手登番 = '' OR 選手登番 IS NULL THEN NULL ELSE CAST(選手登番 AS INTEGER) END,
  CASE WHEN 艇番 = '' OR 艇番 IS NULL THEN NULL ELSE CAST(艇番 AS INTEGER) END,
  CASE WHEN モーター番号 = '' OR モーター番号 IS NULL THEN NULL ELSE CAST(モーター番号 AS INTEGER) END,
  CASE WHEN ボート番号 = '' OR ボート番号 IS NULL THEN NULL ELSE CAST(ボート番号 AS INTEGER) END,
  
  -- 展示タイム（実数変換）
  CASE WHEN 展示 = '' OR 展示 IS NULL THEN NULL ELSE CAST(展示 AS REAL) END,
  
  CASE WHEN 進入 = '' OR 進入 IS NULL THEN NULL ELSE CAST(進入 AS INTEGER) END,
  
  -- スタートタイミング（実数変換）
  CASE WHEN スタートタイミング = '' OR スタートタイミング IS NULL THEN NULL ELSE CAST(スタートタイミング AS REAL) END,
  
  -- レースタイム（文字列のまま）
  CASE WHEN レースタイム = '' OR レースタイム IS NULL THEN NULL ELSE レースタイム END
  
FROM temp_results
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != '';

-- 一時テーブル削除
DROP TABLE temp_results;
EOF

# インポート結果の確認
echo ""
echo "インポート結果確認..."

IMPORTED_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM results;")
echo "インポート件数: $IMPORTED_COUNT 件"

# データ期間の確認
PERIOD_INFO=$(sqlite3 "$DB_FILE" "
SELECT 
  MIN(year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) as start_date,
  MAX(year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) as end_date,
  COUNT(DISTINCT year || month || day || venue_code || race_number) as total_races
FROM results;")

echo "データ期間: $PERIOD_INFO"

# サンプルデータの表示
echo ""
echo "サンプルデータ（最新3件）:"
sqlite3 "$DB_FILE" "
SELECT 
  year || '-' || printf('%02d', month) || '-' || printf('%02d', day) as date,
  venue_code as venue,
  race_number as race,
  racer_number,
  boat_number,
  finish_position
FROM results 
ORDER BY year DESC, month DESC, day DESC, venue_code DESC, race_number DESC 
LIMIT 3;"

echo ""
echo "=== レース結果データ一括インポート完了 ==="
