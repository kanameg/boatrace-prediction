#!/bin/bash
# data/results.csvをSQLiteデータベースにインポートするスクリプト

# データベースファイル
DB_FILE="boat_race.db"
CSV_FILE="../data/results.csv"
SQL_FILE="results.sql"

echo "=== Results CSVインポートスクリプト ==="
echo "データベース: $DB_FILE"
echo "CSVファイル: $CSV_FILE"
echo "SQLファイル: $SQL_FILE"

# ファイル存在チェック
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: CSVファイルが見つかりません: $CSV_FILE"
    exit 1
fi

if [ ! -f "$SQL_FILE" ]; then
    echo "エラー: SQLファイルが見つかりません: $SQL_FILE"
    exit 1
fi

# テーブル作成
echo "テーブルを作成中..."
sqlite3 "$DB_FILE" < "$SQL_FILE"

if [ $? -ne 0 ]; then
    echo "エラー: テーブル作成に失敗しました"
    exit 1
fi

# CSVデータをインポート
echo "CSVデータをインポート中..."
sqlite3 "$DB_FILE" <<EOF
-- 一時テーブル作成
DROP TABLE IF EXISTS temp_results;
CREATE TABLE temp_results (
  年 TEXT,
  月 TEXT,
  日 TEXT,
  レース場番号 TEXT,
  レース番号 TEXT,
  距離 TEXT,
  天候 TEXT,
  風向 TEXT,
  風速 TEXT,
  波高 TEXT,
  単勝_艇番 TEXT,
  単勝_払戻金 TEXT,
  複勝1着_艇番 TEXT,
  複勝1着_払戻金 TEXT,
  複勝2着_艇番 TEXT,
  複勝2着_払戻金 TEXT,
  '2連単_艇番' TEXT,
  '2連単_払戻金' TEXT,
  '2連単_人気' TEXT,
  '2連複_艇番' TEXT,
  '2連複_払戻金' TEXT,
  '2連複_人気' TEXT,
  拡連複1_艇番 TEXT,
  拡連複1_払戻金 TEXT,
  拡連複1_人気 TEXT,
  拡連複2_艇番 TEXT,
  拡連複2_払戻金 TEXT,
  拡連複2_人気 TEXT,
  拡連複3_艇番 TEXT,
  拡連複3_払戻金 TEXT,
  拡連複3_人気 TEXT,
  '3連単_艇番' TEXT,
  '3連単_払戻金' TEXT,
  '3連単_人気' TEXT,
  '3連複_艇番' TEXT,
  '3連複_払戻金' TEXT,
  '3連複_人気' TEXT,
  '1艇_着順' TEXT,
  '1艇_選手登番' TEXT,
  '1艇_艇番' TEXT,
  '1艇_モーター番号' TEXT,
  '1艇_ボート番号' TEXT,
  '1艇_展示' TEXT,
  '1艇_進入' TEXT,
  '1艇_スタートタイミング' TEXT,
  '1艇_レースタイム' TEXT,
  '2艇_着順' TEXT,
  '2艇_選手登番' TEXT,
  '2艇_艇番' TEXT,
  '2艇_モーター番号' TEXT,
  '2艇_ボート番号' TEXT,
  '2艇_展示' TEXT,
  '2艇_進入' TEXT,
  '2艇_スタートタイミング' TEXT,
  '2艇_レースタイム' TEXT,
  '3艇_着順' TEXT,
  '3艇_選手登番' TEXT,
  '3艇_艇番' TEXT,
  '3艇_モーター番号' TEXT,
  '3艇_ボート番号' TEXT,
  '3艇_展示' TEXT,
  '3艇_進入' TEXT,
  '3艇_スタートタイミング' TEXT,
  '3艇_レースタイム' TEXT,
  '4艇_着順' TEXT,
  '4艇_選手登番' TEXT,
  '4艇_艇番' TEXT,
  '4艇_モーター番号' TEXT,
  '4艇_ボート番号' TEXT,
  '4艇_展示' TEXT,
  '4艇_進入' TEXT,
  '4艇_スタートタイミング' TEXT,
  '4艇_レースタイム' TEXT,
  '5艇_着順' TEXT,
  '5艇_選手登番' TEXT,
  '5艇_艇番' TEXT,
  '5艇_モーター番号' TEXT,
  '5艇_ボート番号' TEXT,
  '5艇_展示' TEXT,
  '5艇_進入' TEXT,
  '5艇_スタートタイミング' TEXT,
  '5艇_レースタイム' TEXT,
  '6艇_着順' TEXT,
  '6艇_選手登番' TEXT,
  '6艇_艇番' TEXT,
  '6艇_モーター番号' TEXT,
  '6艇_ボート番号' TEXT,
  '6艇_展示' TEXT,
  '6艇_進入' TEXT,
  '6艇_スタートタイミング' TEXT,
  '6艇_レースタイム' TEXT
);

.mode csv
.headers off
.import $CSV_FILE temp_results

-- 一時テーブルから本テーブルにデータを移行
INSERT INTO results (
  year, month, day, venue_code, race_number, distance, weather, wind_direction, wind_speed, wave_height,
  win_boat_number, win_payout, place_1st_boat_number, place_1st_payout, place_2nd_boat_number, place_2nd_payout,
  exacta_boat_numbers, exacta_payout, exacta_popularity,
  quinella_boat_numbers, quinella_payout, quinella_popularity,
  wide_1_boat_numbers, wide_1_payout, wide_1_popularity,
  wide_2_boat_numbers, wide_2_payout, wide_2_popularity,
  wide_3_boat_numbers, wide_3_payout, wide_3_popularity,
  trifecta_boat_numbers, trifecta_payout, trifecta_popularity,
  trio_boat_numbers, trio_payout, trio_popularity,
  racer1_finish_position, racer1_number, racer1_boat_number, racer1_motor_number, racer1_boat_number_assigned,
  racer1_exhibition_time, racer1_start_course, racer1_start_timing, racer1_race_time,
  racer2_finish_position, racer2_number, racer2_boat_number, racer2_motor_number, racer2_boat_number_assigned,
  racer2_exhibition_time, racer2_start_course, racer2_start_timing, racer2_race_time,
  racer3_finish_position, racer3_number, racer3_boat_number, racer3_motor_number, racer3_boat_number_assigned,
  racer3_exhibition_time, racer3_start_course, racer3_start_timing, racer3_race_time,
  racer4_finish_position, racer4_number, racer4_boat_number, racer4_motor_number, racer4_boat_number_assigned,
  racer4_exhibition_time, racer4_start_course, racer4_start_timing, racer4_race_time,
  racer5_finish_position, racer5_number, racer5_boat_number, racer5_motor_number, racer5_boat_number_assigned,
  racer5_exhibition_time, racer5_start_course, racer5_start_timing, racer5_race_time,
  racer6_finish_position, racer6_number, racer6_boat_number, racer6_motor_number, racer6_boat_number_assigned,
  racer6_exhibition_time, racer6_start_course, racer6_start_timing, racer6_race_time
)
SELECT 
  CAST(年 AS INTEGER), CAST(月 AS INTEGER), CAST(日 AS INTEGER),
  CAST(レース場番号 AS INTEGER), CAST(レース番号 AS INTEGER),
  CAST(距離 AS INTEGER), 天候, 風向, CAST(風速 AS REAL), CAST(波高 AS REAL),
  CASE WHEN 単勝_艇番 = '' OR 単勝_艇番 IS NULL THEN NULL ELSE CAST(単勝_艇番 AS INTEGER) END,
  CASE WHEN 単勝_払戻金 = '' OR 単勝_払戻金 IS NULL THEN NULL ELSE CAST(単勝_払戻金 AS INTEGER) END,
  CASE WHEN 複勝1着_艇番 = '' OR 複勝1着_艇番 IS NULL THEN NULL ELSE CAST(複勝1着_艇番 AS INTEGER) END,
  CASE WHEN 複勝1着_払戻金 = '' OR 複勝1着_払戻金 IS NULL THEN NULL ELSE CAST(複勝1着_払戻金 AS INTEGER) END,
  CASE WHEN 複勝2着_艇番 = '' OR 複勝2着_艇番 IS NULL THEN NULL ELSE CAST(複勝2着_艇番 AS INTEGER) END,
  CASE WHEN 複勝2着_払戻金 = '' OR 複勝2着_払戻金 IS NULL THEN NULL ELSE CAST(複勝2着_払戻金 AS INTEGER) END,
  \`2連単_艇番\`,
  CASE WHEN \`2連単_払戻金\` = '' OR \`2連単_払戻金\` IS NULL THEN NULL ELSE CAST(\`2連単_払戻金\` AS INTEGER) END,
  CASE WHEN \`2連単_人気\` = '' OR \`2連単_人気\` IS NULL THEN NULL ELSE CAST(\`2連単_人気\` AS INTEGER) END,
  \`2連複_艇番\`,
  CASE WHEN \`2連複_払戻金\` = '' OR \`2連複_払戻金\` IS NULL THEN NULL ELSE CAST(\`2連複_払戻金\` AS INTEGER) END,
  CASE WHEN \`2連複_人気\` = '' OR \`2連複_人気\` IS NULL THEN NULL ELSE CAST(\`2連複_人気\` AS INTEGER) END,
  拡連複1_艇番,
  CASE WHEN 拡連複1_払戻金 = '' OR 拡連複1_払戻金 IS NULL THEN NULL ELSE CAST(拡連複1_払戻金 AS INTEGER) END,
  CASE WHEN 拡連複1_人気 = '' OR 拡連複1_人気 IS NULL THEN NULL ELSE CAST(拡連複1_人気 AS INTEGER) END,
  拡連複2_艇番,
  CASE WHEN 拡連複2_払戻金 = '' OR 拡連複2_払戻金 IS NULL THEN NULL ELSE CAST(拡連複2_払戻金 AS INTEGER) END,
  CASE WHEN 拡連複2_人気 = '' OR 拡連複2_人気 IS NULL THEN NULL ELSE CAST(拡連複2_人気 AS INTEGER) END,
  拡連複3_艇番,
  CASE WHEN 拡連複3_払戻金 = '' OR 拡連複3_払戻金 IS NULL THEN NULL ELSE CAST(拡連複3_払戻金 AS INTEGER) END,
  CASE WHEN 拡連複3_人気 = '' OR 拡連複3_人気 IS NULL THEN NULL ELSE CAST(拡連複3_人気 AS INTEGER) END,
  \`3連単_艇番\`,
  CASE WHEN \`3連単_払戻金\` = '' OR \`3連単_払戻金\` IS NULL THEN NULL ELSE CAST(\`3連単_払戻金\` AS INTEGER) END,
  CASE WHEN \`3連単_人気\` = '' OR \`3連単_人気\` IS NULL THEN NULL ELSE CAST(\`3連単_人気\` AS INTEGER) END,
  \`3連複_艇番\`,
  CASE WHEN \`3連複_払戻金\` = '' OR \`3連複_払戻金\` IS NULL THEN NULL ELSE CAST(\`3連複_払戻金\` AS INTEGER) END,
  CASE WHEN \`3連複_人気\` = '' OR \`3連複_人気\` IS NULL THEN NULL ELSE CAST(\`3連複_人気\` AS INTEGER) END,
  CASE WHEN \`1艇_着順\` = '' OR \`1艇_着順\` IS NULL THEN NULL ELSE CAST(\`1艇_着順\` AS INTEGER) END,
  CASE WHEN \`1艇_選手登番\` = '' OR \`1艇_選手登番\` IS NULL THEN NULL ELSE CAST(\`1艇_選手登番\` AS INTEGER) END,
  CASE WHEN \`1艇_艇番\` = '' OR \`1艇_艇番\` IS NULL THEN NULL ELSE CAST(\`1艇_艇番\` AS INTEGER) END,
  CASE WHEN \`1艇_モーター番号\` = '' OR \`1艇_モーター番号\` IS NULL THEN NULL ELSE CAST(\`1艇_モーター番号\` AS INTEGER) END,
  CASE WHEN \`1艇_ボート番号\` = '' OR \`1艇_ボート番号\` IS NULL THEN NULL ELSE CAST(\`1艇_ボート番号\` AS INTEGER) END,
  CASE WHEN \`1艇_展示\` = '' OR \`1艇_展示\` IS NULL THEN NULL ELSE CAST(\`1艇_展示\` AS REAL) END,
  CASE WHEN \`1艇_進入\` = '' OR \`1艇_進入\` IS NULL THEN NULL ELSE CAST(\`1艇_進入\` AS INTEGER) END,
  CASE WHEN \`1艇_スタートタイミング\` = '' OR \`1艇_スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`1艇_スタートタイミング\` AS REAL) END,
  CASE WHEN \`1艇_レースタイム\` = '' OR \`1艇_レースタイム\` IS NULL THEN NULL ELSE CAST(\`1艇_レースタイム\` AS REAL) END,
  CASE WHEN \`2艇_着順\` = '' OR \`2艇_着順\` IS NULL THEN NULL ELSE CAST(\`2艇_着順\` AS INTEGER) END,
  CASE WHEN \`2艇_選手登番\` = '' OR \`2艇_選手登番\` IS NULL THEN NULL ELSE CAST(\`2艇_選手登番\` AS INTEGER) END,
  CASE WHEN \`2艇_艇番\` = '' OR \`2艇_艇番\` IS NULL THEN NULL ELSE CAST(\`2艇_艇番\` AS INTEGER) END,
  CASE WHEN \`2艇_モーター番号\` = '' OR \`2艇_モーター番号\` IS NULL THEN NULL ELSE CAST(\`2艇_モーター番号\` AS INTEGER) END,
  CASE WHEN \`2艇_ボート番号\` = '' OR \`2艇_ボート番号\` IS NULL THEN NULL ELSE CAST(\`2艇_ボート番号\` AS INTEGER) END,
  CASE WHEN \`2艇_展示\` = '' OR \`2艇_展示\` IS NULL THEN NULL ELSE CAST(\`2艇_展示\` AS REAL) END,
  CASE WHEN \`2艇_進入\` = '' OR \`2艇_進入\` IS NULL THEN NULL ELSE CAST(\`2艇_進入\` AS INTEGER) END,
  CASE WHEN \`2艇_スタートタイミング\` = '' OR \`2艇_スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`2艇_スタートタイミング\` AS REAL) END,
  CASE WHEN \`2艇_レースタイム\` = '' OR \`2艇_レースタイム\` IS NULL THEN NULL ELSE CAST(\`2艇_レースタイム\` AS REAL) END,
  CASE WHEN \`3艇_着順\` = '' OR \`3艇_着順\` IS NULL THEN NULL ELSE CAST(\`3艇_着順\` AS INTEGER) END,
  CASE WHEN \`3艇_選手登番\` = '' OR \`3艇_選手登番\` IS NULL THEN NULL ELSE CAST(\`3艇_選手登番\` AS INTEGER) END,
  CASE WHEN \`3艇_艇番\` = '' OR \`3艇_艇番\` IS NULL THEN NULL ELSE CAST(\`3艇_艇番\` AS INTEGER) END,
  CASE WHEN \`3艇_モーター番号\` = '' OR \`3艇_モーター番号\` IS NULL THEN NULL ELSE CAST(\`3艇_モーター番号\` AS INTEGER) END,
  CASE WHEN \`3艇_ボート番号\` = '' OR \`3艇_ボート番号\` IS NULL THEN NULL ELSE CAST(\`3艇_ボート番号\` AS INTEGER) END,
  CASE WHEN \`3艇_展示\` = '' OR \`3艇_展示\` IS NULL THEN NULL ELSE CAST(\`3艇_展示\` AS REAL) END,
  CASE WHEN \`3艇_進入\` = '' OR \`3艇_進入\` IS NULL THEN NULL ELSE CAST(\`3艇_進入\` AS INTEGER) END,
  CASE WHEN \`3艇_スタートタイミング\` = '' OR \`3艇_スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`3艇_スタートタイミング\` AS REAL) END,
  CASE WHEN \`3艇_レースタイム\` = '' OR \`3艇_レースタイム\` IS NULL THEN NULL ELSE CAST(\`3艇_レースタイム\` AS REAL) END,
  CASE WHEN \`4艇_着順\` = '' OR \`4艇_着順\` IS NULL THEN NULL ELSE CAST(\`4艇_着順\` AS INTEGER) END,
  CASE WHEN \`4艇_選手登番\` = '' OR \`4艇_選手登番\` IS NULL THEN NULL ELSE CAST(\`4艇_選手登番\` AS INTEGER) END,
  CASE WHEN \`4艇_艇番\` = '' OR \`4艇_艇番\` IS NULL THEN NULL ELSE CAST(\`4艇_艇番\` AS INTEGER) END,
  CASE WHEN \`4艇_モーター番号\` = '' OR \`4艇_モーター番号\` IS NULL THEN NULL ELSE CAST(\`4艇_モーター番号\` AS INTEGER) END,
  CASE WHEN \`4艇_ボート番号\` = '' OR \`4艇_ボート番号\` IS NULL THEN NULL ELSE CAST(\`4艇_ボート番号\` AS INTEGER) END,
  CASE WHEN \`4艇_展示\` = '' OR \`4艇_展示\` IS NULL THEN NULL ELSE CAST(\`4艇_展示\` AS REAL) END,
  CASE WHEN \`4艇_進入\` = '' OR \`4艇_進入\` IS NULL THEN NULL ELSE CAST(\`4艇_進入\` AS INTEGER) END,
  CASE WHEN \`4艇_スタートタイミング\` = '' OR \`4艇_スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`4艇_スタートタイミング\` AS REAL) END,
  CASE WHEN \`4艇_レースタイム\` = '' OR \`4艇_レースタイム\` IS NULL THEN NULL ELSE CAST(\`4艇_レースタイム\` AS REAL) END,
  CASE WHEN \`5艇_着順\` = '' OR \`5艇_着順\` IS NULL THEN NULL ELSE CAST(\`5艇_着順\` AS INTEGER) END,
  CASE WHEN \`5艇_選手登番\` = '' OR \`5艇_選手登番\` IS NULL THEN NULL ELSE CAST(\`5艇_選手登番\` AS INTEGER) END,
  CASE WHEN \`5艇_艇番\` = '' OR \`5艇_艇番\` IS NULL THEN NULL ELSE CAST(\`5艇_艇番\` AS INTEGER) END,
  CASE WHEN \`5艇_モーター番号\` = '' OR \`5艇_モーター番号\` IS NULL THEN NULL ELSE CAST(\`5艇_モーター番号\` AS INTEGER) END,
  CASE WHEN \`5艇_ボート番号\` = '' OR \`5艇_ボート番号\` IS NULL THEN NULL ELSE CAST(\`5艇_ボート番号\` AS INTEGER) END,
  CASE WHEN \`5艇_展示\` = '' OR \`5艇_展示\` IS NULL THEN NULL ELSE CAST(\`5艇_展示\` AS REAL) END,
  CASE WHEN \`5艇_進入\` = '' OR \`5艇_進入\` IS NULL THEN NULL ELSE CAST(\`5艇_進入\` AS INTEGER) END,
  CASE WHEN \`5艇_スタートタイミング\` = '' OR \`5艇_スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`5艇_スタートタイミング\` AS REAL) END,
  CASE WHEN \`5艇_レースタイム\` = '' OR \`5艇_レースタイム\` IS NULL THEN NULL ELSE CAST(\`5艇_レースタイム\` AS REAL) END,
  CASE WHEN \`6艇_着順\` = '' OR \`6艇_着順\` IS NULL THEN NULL ELSE CAST(\`6艇_着順\` AS INTEGER) END,
  CASE WHEN \`6艇_選手登番\` = '' OR \`6艇_選手登番\` IS NULL THEN NULL ELSE CAST(\`6艇_選手登番\` AS INTEGER) END,
  CASE WHEN \`6艇_艇番\` = '' OR \`6艇_艇番\` IS NULL THEN NULL ELSE CAST(\`6艇_艇番\` AS INTEGER) END,
  CASE WHEN \`6艇_モーター番号\` = '' OR \`6艇_モーター番号\` IS NULL THEN NULL ELSE CAST(\`6艇_モーター番号\` AS INTEGER) END,
  CASE WHEN \`6艇_ボート番号\` = '' OR \`6艇_ボート番号\` IS NULL THEN NULL ELSE CAST(\`6艇_ボート番号\` AS INTEGER) END,
  CASE WHEN \`6艇_展示\` = '' OR \`6艇_展示\` IS NULL THEN NULL ELSE CAST(\`6艇_展示\` AS REAL) END,
  CASE WHEN \`6艇_進入\` = '' OR \`6艇_進入\` IS NULL THEN NULL ELSE CAST(\`6艇_進入\` AS INTEGER) END,
  CASE WHEN \`6艇_スタートタイミング\` = '' OR \`6艇_スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`6艇_スタートタイミング\` AS REAL) END,
  CASE WHEN \`6艇_レースタイム\` = '' OR \`6艇_レースタイム\` IS NULL THEN NULL ELSE CAST(\`6艇_レースタイム\` AS REAL) END
FROM temp_results
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != '';

-- 一時テーブルを削除
DROP TABLE temp_results;
EOF

if [ $? -ne 0 ]; then
    echo "エラー: CSVインポートに失敗しました"
    exit 1
fi

# インポート結果確認
RECORD_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM results;")
echo "インポート完了: $RECORD_COUNT 件のレコードが追加されました"

echo "=== インポート完了 ==="
