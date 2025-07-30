#!/bin/bash

# レーサー期別成績データ増分インポートスクリプト
# data/racers.csvから新規データのみをSQLite3データベースに追加する

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_FILE="${SCRIPT_DIR}/../data/racers.csv"
DB_FILE="${SCRIPT_DIR}/boat_race.db"

echo "=== レーサー期別成績データ増分インポート開始 ==="

# CSVファイルの存在確認
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: $CSV_FILE が見つかりません"
    exit 1
fi

# データベースファイルの存在確認
if [ ! -f "$DB_FILE" ]; then
    echo "エラー: データベース $DB_FILE が見つかりません"
    echo "先に import_racers.sh を実行してください"
    exit 1
fi

echo "CSVファイル: $CSV_FILE"
echo "データベース: $DB_FILE"

# CSVの行数を確認
CSV_LINES=$(wc -l < "$CSV_FILE")
echo "CSVファイル行数: $CSV_LINES 行（ヘッダー含む）"

# 現在のデータベース件数を確認
CURRENT_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM racers;")
echo "現在のDB件数: $CURRENT_COUNT 件"

# 増分インポート実行
echo ""
echo "増分インポートを実行中..."

sqlite3 "$DB_FILE" <<EOF
-- 一時テーブル作成
DROP TABLE IF EXISTS temp_racers_incremental;
CREATE TABLE temp_racers_incremental (
  年 INTEGER,
  期 TEXT,
  登番 INTEGER,
  名前漢字 TEXT,
  名前カナ TEXT,
  支部 TEXT,
  級 TEXT,
  年号 TEXT,
  生年月日 TEXT,
  性別 INTEGER,
  年齢 INTEGER,
  身長 INTEGER,
  体重 INTEGER,
  血液型 TEXT,
  勝率 REAL,
  複勝率 REAL,
  "1着回数" INTEGER,
  "2着回数" INTEGER,
  出走回数 INTEGER,
  優出回数 INTEGER,
  優勝回数 INTEGER,
  平均スタートタイミング REAL,
  "1コース進入回数" INTEGER,
  "1コース複勝率" REAL,
  "1コース平均スタートタイミング" REAL,
  "1コース平均スタート順位" REAL,
  "2コース進入回数" INTEGER,
  "2コース複勝率" REAL,
  "2コース平均スタートタイミング" REAL,
  "2コース平均スタート順位" REAL,
  "3コース進入回数" INTEGER,
  "3コース複勝率" REAL,
  "3コース平均スタートタイミング" REAL,
  "3コース平均スタート順位" REAL,
  "4コース進入回数" INTEGER,
  "4コース複勝率" REAL,
  "4コース平均スタートタイミング" REAL,
  "4コース平均スタート順位" REAL,
  "5コース進入回数" INTEGER,
  "5コース複勝率" REAL,
  "5コース平均スタートタイミング" REAL,
  "5コース平均スタート順位" REAL,
  "6コース進入回数" INTEGER,
  "6コース複勝率" REAL,
  "6コース平均スタートタイミング" REAL,
  "6コース平均スタート順位" REAL,
  前期級 TEXT,
  前々期級 TEXT,
  前々々期級 TEXT,
  前期能力指数 REAL,
  今期能力指数 REAL,
  集計開始日 TEXT,
  集計終了日 TEXT,
  "期" TEXT,
  "1コース1着" INTEGER, "1コース2着" INTEGER, "1コース3着" INTEGER, "1コース4着" INTEGER, "1コース5着" INTEGER, "1コース6着" INTEGER,
  "1コースF" INTEGER, "1コースL0" INTEGER, "1コースL1" INTEGER, "1コースK0" INTEGER, "1コースK1" INTEGER, "1コースS0" INTEGER, "1コースS1" INTEGER, "1コースS2" INTEGER,
  "2コース1着" INTEGER, "2コース2着" INTEGER, "2コース3着" INTEGER, "2コース4着" INTEGER, "2コース5着" INTEGER, "2コース6着" INTEGER,
  "2コースF" INTEGER, "2コースL0" INTEGER, "2コースL1" INTEGER, "2コースK0" INTEGER, "2コースK1" INTEGER, "2コースS0" INTEGER, "2コースS1" INTEGER, "2コースS2" INTEGER,
  "3コース1着" INTEGER, "3コース2着" INTEGER, "3コース3着" INTEGER, "3コース4着" INTEGER, "3コース5着" INTEGER, "3コース6着" INTEGER,
  "3コースF" INTEGER, "3コースL0" INTEGER, "3コースL1" INTEGER, "3コースK0" INTEGER, "3コースK1" INTEGER, "3コースS0" INTEGER, "3コースS1" INTEGER, "3コースS2" INTEGER,
  "4コース1着" INTEGER, "4コース2着" INTEGER, "4コース3着" INTEGER, "4コース4着" INTEGER, "4コース5着" INTEGER, "4コース6着" INTEGER,
  "4コースF" INTEGER, "4コースL0" INTEGER, "4コースL1" INTEGER, "4コースK0" INTEGER, "4コースK1" INTEGER, "4コースS0" INTEGER, "4コースS1" INTEGER, "4コースS2" INTEGER,
  "5コース1着" INTEGER, "5コース2着" INTEGER, "5コース3着" INTEGER, "5コース4着" INTEGER, "5コース5着" INTEGER, "5コース6着" INTEGER,
  "5コースF" INTEGER, "5コースL0" INTEGER, "5コースL1" INTEGER, "5コースK0" INTEGER, "5コースK1" INTEGER, "5コースS0" INTEGER, "5コースS1" INTEGER, "5コースS2" INTEGER,
  "6コース1着" INTEGER, "6コース2着" INTEGER, "6コース3着" INTEGER, "6コース4着" INTEGER, "6コース5着" INTEGER, "6コース6着" INTEGER,
  "6コースF" INTEGER, "6コースL0" INTEGER, "6コースL1" INTEGER, "6コースK0" INTEGER, "6コースK1" INTEGER, "6コースS0" INTEGER, "6コースS1" INTEGER, "6コースS2" INTEGER,
  コース無L0 INTEGER, コース無L1 INTEGER, コース無K0 INTEGER, コース無K1 INTEGER,
  出身地 TEXT
);

-- CSVファイルをインポート
.mode csv
.headers on
.import '$CSV_FILE' temp_racers_incremental

-- 新規データのみを抽出して本テーブルに挿入
INSERT OR IGNORE INTO racers (
  year, period, racer_number, name_kanji, name_kana, branch, class, year_name, birth_date, gender,
  age, height, weight, blood_type, win_rate, quinella_rate, first_place_count, second_place_count,
  total_races, excellent_race_count, victory_count, avg_start_timing,
  course1_entries, course1_quinella_rate, course1_avg_start_timing, course1_avg_start_order,
  course2_entries, course2_quinella_rate, course2_avg_start_timing, course2_avg_start_order,
  course3_entries, course3_quinella_rate, course3_avg_start_timing, course3_avg_start_order,
  course4_entries, course4_quinella_rate, course4_avg_start_timing, course4_avg_start_order,
  course5_entries, course5_quinella_rate, course5_avg_start_timing, course5_avg_start_order,
  course6_entries, course6_quinella_rate, course6_avg_start_timing, course6_avg_start_order,
  previous_class, previous_previous_class, previous_previous_previous_class,
  previous_ability_index, current_ability_index,
  calculation_start_date, calculation_end_date, training_period,
  course1_1st, course1_2nd, course1_3rd, course1_4th, course1_5th, course1_6th,
  course1_f, course1_l0, course1_l1, course1_k0, course1_k1, course1_s0, course1_s1, course1_s2,
  course2_1st, course2_2nd, course2_3rd, course2_4th, course2_5th, course2_6th,
  course2_f, course2_l0, course2_l1, course2_k0, course2_k1, course2_s0, course2_s1, course2_s2,
  course3_1st, course3_2nd, course3_3rd, course3_4th, course3_5th, course3_6th,
  course3_f, course3_l0, course3_l1, course3_k0, course3_k1, course3_s0, course3_s1, course3_s2,
  course4_1st, course4_2nd, course4_3rd, course4_4th, course4_5th, course4_6th,
  course4_f, course4_l0, course4_l1, course4_k0, course4_k1, course4_s0, course4_s1, course4_s2,
  course5_1st, course5_2nd, course5_3rd, course5_4th, course5_5th, course5_6th,
  course5_f, course5_l0, course5_l1, course5_k0, course5_k1, course5_s0, course5_s1, course5_s2,
  course6_1st, course6_2nd, course6_3rd, course6_4th, course6_5th, course6_6th,
  course6_f, course6_l0, course6_l1, course6_k0, course6_k1, course6_s0, course6_s1, course6_s2,
  no_course_l0, no_course_l1, no_course_k0, no_course_k1, birthplace
)
SELECT 
  CASE WHEN 年 = '' OR 年 IS NULL THEN NULL ELSE CAST(年 AS INTEGER) END,
  期,
  CASE WHEN 登番 = '' OR 登番 IS NULL THEN NULL ELSE CAST(登番 AS INTEGER) END,
  名前漢字, 名前カナ, 支部, 級, 年号, 生年月日,
  CASE WHEN 性別 = '' OR 性別 IS NULL THEN NULL ELSE CAST(性別 AS INTEGER) END,
  CASE WHEN 年齢 = '' OR 年齢 IS NULL THEN NULL ELSE CAST(年齢 AS INTEGER) END,
  CASE WHEN 身長 = '' OR 身長 IS NULL THEN NULL ELSE CAST(身長 AS INTEGER) END,
  CASE WHEN 体重 = '' OR 体重 IS NULL THEN NULL ELSE CAST(体重 AS INTEGER) END,
  血液型,
  CASE WHEN 勝率 = '' OR 勝率 IS NULL THEN NULL ELSE CAST(勝率 AS REAL) END,
  CASE WHEN 複勝率 = '' OR 複勝率 IS NULL THEN NULL ELSE CAST(複勝率 AS REAL) END,
  CASE WHEN "1着回数" = '' OR "1着回数" IS NULL THEN NULL ELSE CAST("1着回数" AS INTEGER) END,
  CASE WHEN "2着回数" = '' OR "2着回数" IS NULL THEN NULL ELSE CAST("2着回数" AS INTEGER) END,
  CASE WHEN 出走回数 = '' OR 出走回数 IS NULL THEN NULL ELSE CAST(出走回数 AS INTEGER) END,
  CASE WHEN 優出回数 = '' OR 優出回数 IS NULL THEN NULL ELSE CAST(優出回数 AS INTEGER) END,
  CASE WHEN 優勝回数 = '' OR 優勝回数 IS NULL THEN NULL ELSE CAST(優勝回数 AS INTEGER) END,
  CASE WHEN 平均スタートタイミング = '' OR 平均スタートタイミング IS NULL THEN NULL ELSE CAST(平均スタートタイミング AS REAL) END,
  CASE WHEN "1コース進入回数" = '' OR "1コース進入回数" IS NULL THEN NULL ELSE CAST("1コース進入回数" AS INTEGER) END,
  CASE WHEN "1コース複勝率" = '' OR "1コース複勝率" IS NULL THEN NULL ELSE CAST("1コース複勝率" AS REAL) END,
  CASE WHEN "1コース平均スタートタイミング" = '' OR "1コース平均スタートタイミング" IS NULL THEN NULL ELSE CAST("1コース平均スタートタイミング" AS REAL) END,
  CASE WHEN "1コース平均スタート順位" = '' OR "1コース平均スタート順位" IS NULL THEN NULL ELSE CAST("1コース平均スタート順位" AS REAL) END,
  CASE WHEN "2コース進入回数" = '' OR "2コース進入回数" IS NULL THEN NULL ELSE CAST("2コース進入回数" AS INTEGER) END,
  CASE WHEN "2コース複勝率" = '' OR "2コース複勝率" IS NULL THEN NULL ELSE CAST("2コース複勝率" AS REAL) END,
  CASE WHEN "2コース平均スタートタイミング" = '' OR "2コース平均スタートタイミング" IS NULL THEN NULL ELSE CAST("2コース平均スタートタイミング" AS REAL) END,
  CASE WHEN "2コース平均スタート順位" = '' OR "2コース平均スタート順位" IS NULL THEN NULL ELSE CAST("2コース平均スタート順位" AS REAL) END,
  CASE WHEN "3コース進入回数" = '' OR "3コース進入回数" IS NULL THEN NULL ELSE CAST("3コース進入回数" AS INTEGER) END,
  CASE WHEN "3コース複勝率" = '' OR "3コース複勝率" IS NULL THEN NULL ELSE CAST("3コース複勝率" AS REAL) END,
  CASE WHEN "3コース平均スタートタイミング" = '' OR "3コース平均スタートタイミング" IS NULL THEN NULL ELSE CAST("3コース平均スタートタイミング" AS REAL) END,
  CASE WHEN "3コース平均スタート順位" = '' OR "3コース平均スタート順位" IS NULL THEN NULL ELSE CAST("3コース平均スタート順位" AS REAL) END,
  CASE WHEN "4コース進入回数" = '' OR "4コース進入回数" IS NULL THEN NULL ELSE CAST("4コース進入回数" AS INTEGER) END,
  CASE WHEN "4コース複勝率" = '' OR "4コース複勝率" IS NULL THEN NULL ELSE CAST("4コース複勝率" AS REAL) END,
  CASE WHEN "4コース平均スタートタイミング" = '' OR "4コース平均スタートタイミング" IS NULL THEN NULL ELSE CAST("4コース平均スタートタイミング" AS REAL) END,
  CASE WHEN "4コース平均スタート順位" = '' OR "4コース平均スタート順位" IS NULL THEN NULL ELSE CAST("4コース平均スタート順位" AS REAL) END,
  CASE WHEN "5コース進入回数" = '' OR "5コース進入回数" IS NULL THEN NULL ELSE CAST("5コース進入回数" AS INTEGER) END,
  CASE WHEN "5コース複勝率" = '' OR "5コース複勝率" IS NULL THEN NULL ELSE CAST("5コース複勝率" AS REAL) END,
  CASE WHEN "5コース平均スタートタイミング" = '' OR "5コース平均スタートタイミング" IS NULL THEN NULL ELSE CAST("5コース平均スタートタイミング" AS REAL) END,
  CASE WHEN "5コース平均スタート順位" = '' OR "5コース平均スタート順位" IS NULL THEN NULL ELSE CAST("5コース平均スタート順位" AS REAL) END,
  CASE WHEN "6コース進入回数" = '' OR "6コース進入回数" IS NULL THEN NULL ELSE CAST("6コース進入回数" AS INTEGER) END,
  CASE WHEN "6コース複勝率" = '' OR "6コース複勝率" IS NULL THEN NULL ELSE CAST("6コース複勝率" AS REAL) END,
  CASE WHEN "6コース平均スタートタイミング" = '' OR "6コース平均スタートタイミング" IS NULL THEN NULL ELSE CAST("6コース平均スタートタイミング" AS REAL) END,
  CASE WHEN "6コース平均スタート順位" = '' OR "6コース平均スタート順位" IS NULL THEN NULL ELSE CAST("6コース平均スタート順位" AS REAL) END,
  前期級, 前々期級, 前々々期級,
  前期能力指数, 今期能力指数,
  集計開始日, 集計終了日, 期,
  CASE WHEN "1コース1着" = '' OR "1コース1着" IS NULL THEN NULL ELSE CAST("1コース1着" AS INTEGER) END,
  CASE WHEN "1コース2着" = '' OR "1コース2着" IS NULL THEN NULL ELSE CAST("1コース2着" AS INTEGER) END,
  CASE WHEN "1コース3着" = '' OR "1コース3着" IS NULL THEN NULL ELSE CAST("1コース3着" AS INTEGER) END,
  CASE WHEN "1コース4着" = '' OR "1コース4着" IS NULL THEN NULL ELSE CAST("1コース4着" AS INTEGER) END,
  CASE WHEN "1コース5着" = '' OR "1コース5着" IS NULL THEN NULL ELSE CAST("1コース5着" AS INTEGER) END,
  CASE WHEN "1コース6着" = '' OR "1コース6着" IS NULL THEN NULL ELSE CAST("1コース6着" AS INTEGER) END,
  CASE WHEN "1コースF" = '' OR "1コースF" IS NULL THEN NULL ELSE CAST("1コースF" AS INTEGER) END,
  CASE WHEN "1コースL0" = '' OR "1コースL0" IS NULL THEN NULL ELSE CAST("1コースL0" AS INTEGER) END,
  CASE WHEN "1コースL1" = '' OR "1コースL1" IS NULL THEN NULL ELSE CAST("1コースL1" AS INTEGER) END,
  CASE WHEN "1コースK0" = '' OR "1コースK0" IS NULL THEN NULL ELSE CAST("1コースK0" AS INTEGER) END,
  CASE WHEN "1コースK1" = '' OR "1コースK1" IS NULL THEN NULL ELSE CAST("1コースK1" AS INTEGER) END,
  CASE WHEN "1コースS0" = '' OR "1コースS0" IS NULL THEN NULL ELSE CAST("1コースS0" AS INTEGER) END,
  CASE WHEN "1コースS1" = '' OR "1コースS1" IS NULL THEN NULL ELSE CAST("1コースS1" AS INTEGER) END,
  CASE WHEN "1コースS2" = '' OR "1コースS2" IS NULL THEN NULL ELSE CAST("1コースS2" AS INTEGER) END,
  CASE WHEN "2コース1着" = '' OR "2コース1着" IS NULL THEN NULL ELSE CAST("2コース1着" AS INTEGER) END,
  CASE WHEN "2コース2着" = '' OR "2コース2着" IS NULL THEN NULL ELSE CAST("2コース2着" AS INTEGER) END,
  CASE WHEN "2コース3着" = '' OR "2コース3着" IS NULL THEN NULL ELSE CAST("2コース3着" AS INTEGER) END,
  CASE WHEN "2コース4着" = '' OR "2コース4着" IS NULL THEN NULL ELSE CAST("2コース4着" AS INTEGER) END,
  CASE WHEN "2コース5着" = '' OR "2コース5着" IS NULL THEN NULL ELSE CAST("2コース5着" AS INTEGER) END,
  CASE WHEN "2コース6着" = '' OR "2コース6着" IS NULL THEN NULL ELSE CAST("2コース6着" AS INTEGER) END,
  CASE WHEN "2コースF" = '' OR "2コースF" IS NULL THEN NULL ELSE CAST("2コースF" AS INTEGER) END,
  CASE WHEN "2コースL0" = '' OR "2コースL0" IS NULL THEN NULL ELSE CAST("2コースL0" AS INTEGER) END,
  CASE WHEN "2コースL1" = '' OR "2コースL1" IS NULL THEN NULL ELSE CAST("2コースL1" AS INTEGER) END,
  CASE WHEN "2コースK0" = '' OR "2コースK0" IS NULL THEN NULL ELSE CAST("2コースK0" AS INTEGER) END,
  CASE WHEN "2コースK1" = '' OR "2コースK1" IS NULL THEN NULL ELSE CAST("2コースK1" AS INTEGER) END,
  CASE WHEN "2コースS0" = '' OR "2コースS0" IS NULL THEN NULL ELSE CAST("2コースS0" AS INTEGER) END,
  CASE WHEN "2コースS1" = '' OR "2コースS1" IS NULL THEN NULL ELSE CAST("2コースS1" AS INTEGER) END,
  CASE WHEN "2コースS2" = '' OR "2コースS2" IS NULL THEN NULL ELSE CAST("2コースS2" AS INTEGER) END,
  CASE WHEN "3コース1着" = '' OR "3コース1着" IS NULL THEN NULL ELSE CAST("3コース1着" AS INTEGER) END,
  CASE WHEN "3コース2着" = '' OR "3コース2着" IS NULL THEN NULL ELSE CAST("3コース2着" AS INTEGER) END,
  CASE WHEN "3コース3着" = '' OR "3コース3着" IS NULL THEN NULL ELSE CAST("3コース3着" AS INTEGER) END,
  CASE WHEN "3コース4着" = '' OR "3コース4着" IS NULL THEN NULL ELSE CAST("3コース4着" AS INTEGER) END,
  CASE WHEN "3コース5着" = '' OR "3コース5着" IS NULL THEN NULL ELSE CAST("3コース5着" AS INTEGER) END,
  CASE WHEN "3コース6着" = '' OR "3コース6着" IS NULL THEN NULL ELSE CAST("3コース6着" AS INTEGER) END,
  CASE WHEN "3コースF" = '' OR "3コースF" IS NULL THEN NULL ELSE CAST("3コースF" AS INTEGER) END,
  CASE WHEN "3コースL0" = '' OR "3コースL0" IS NULL THEN NULL ELSE CAST("3コースL0" AS INTEGER) END,
  CASE WHEN "3コースL1" = '' OR "3コースL1" IS NULL THEN NULL ELSE CAST("3コースL1" AS INTEGER) END,
  CASE WHEN "3コースK0" = '' OR "3コースK0" IS NULL THEN NULL ELSE CAST("3コースK0" AS INTEGER) END,
  CASE WHEN "3コースK1" = '' OR "3コースK1" IS NULL THEN NULL ELSE CAST("3コースK1" AS INTEGER) END,
  CASE WHEN "3コースS0" = '' OR "3コースS0" IS NULL THEN NULL ELSE CAST("3コースS0" AS INTEGER) END,
  CASE WHEN "3コースS1" = '' OR "3コースS1" IS NULL THEN NULL ELSE CAST("3コースS1" AS INTEGER) END,
  CASE WHEN "3コースS2" = '' OR "3コースS2" IS NULL THEN NULL ELSE CAST("3コースS2" AS INTEGER) END,
  CASE WHEN "4コース1着" = '' OR "4コース1着" IS NULL THEN NULL ELSE CAST("4コース1着" AS INTEGER) END,
  CASE WHEN "4コース2着" = '' OR "4コース2着" IS NULL THEN NULL ELSE CAST("4コース2着" AS INTEGER) END,
  CASE WHEN "4コース3着" = '' OR "4コース3着" IS NULL THEN NULL ELSE CAST("4コース3着" AS INTEGER) END,
  CASE WHEN "4コース4着" = '' OR "4コース4着" IS NULL THEN NULL ELSE CAST("4コース4着" AS INTEGER) END,
  CASE WHEN "4コース5着" = '' OR "4コース5着" IS NULL THEN NULL ELSE CAST("4コース5着" AS INTEGER) END,
  CASE WHEN "4コース6着" = '' OR "4コース6着" IS NULL THEN NULL ELSE CAST("4コース6着" AS INTEGER) END,
  CASE WHEN "4コースF" = '' OR "4コースF" IS NULL THEN NULL ELSE CAST("4コースF" AS INTEGER) END,
  CASE WHEN "4コースL0" = '' OR "4コースL0" IS NULL THEN NULL ELSE CAST("4コースL0" AS INTEGER) END,
  CASE WHEN "4コースL1" = '' OR "4コースL1" IS NULL THEN NULL ELSE CAST("4コースL1" AS INTEGER) END,
  CASE WHEN "4コースK0" = '' OR "4コースK0" IS NULL THEN NULL ELSE CAST("4コースK0" AS INTEGER) END,
  CASE WHEN "4コースK1" = '' OR "4コースK1" IS NULL THEN NULL ELSE CAST("4コースK1" AS INTEGER) END,
  CASE WHEN "4コースS0" = '' OR "4コースS0" IS NULL THEN NULL ELSE CAST("4コースS0" AS INTEGER) END,
  CASE WHEN "4コースS1" = '' OR "4コースS1" IS NULL THEN NULL ELSE CAST("4コースS1" AS INTEGER) END,
  CASE WHEN "4コースS2" = '' OR "4コースS2" IS NULL THEN NULL ELSE CAST("4コースS2" AS INTEGER) END,
  CASE WHEN "5コース1着" = '' OR "5コース1着" IS NULL THEN NULL ELSE CAST("5コース1着" AS INTEGER) END,
  CASE WHEN "5コース2着" = '' OR "5コース2着" IS NULL THEN NULL ELSE CAST("5コース2着" AS INTEGER) END,
  CASE WHEN "5コース3着" = '' OR "5コース3着" IS NULL THEN NULL ELSE CAST("5コース3着" AS INTEGER) END,
  CASE WHEN "5コース4着" = '' OR "5コース4着" IS NULL THEN NULL ELSE CAST("5コース4着" AS INTEGER) END,
  CASE WHEN "5コース5着" = '' OR "5コース5着" IS NULL THEN NULL ELSE CAST("5コース5着" AS INTEGER) END,
  CASE WHEN "5コース6着" = '' OR "5コース6着" IS NULL THEN NULL ELSE CAST("5コース6着" AS INTEGER) END,
  CASE WHEN "5コースF" = '' OR "5コースF" IS NULL THEN NULL ELSE CAST("5コースF" AS INTEGER) END,
  CASE WHEN "5コースL0" = '' OR "5コースL0" IS NULL THEN NULL ELSE CAST("5コースL0" AS INTEGER) END,
  CASE WHEN "5コースL1" = '' OR "5コースL1" IS NULL THEN NULL ELSE CAST("5コースL1" AS INTEGER) END,
  CASE WHEN "5コースK0" = '' OR "5コースK0" IS NULL THEN NULL ELSE CAST("5コースK0" AS INTEGER) END,
  CASE WHEN "5コースK1" = '' OR "5コースK1" IS NULL THEN NULL ELSE CAST("5コースK1" AS INTEGER) END,
  CASE WHEN "5コースS0" = '' OR "5コースS0" IS NULL THEN NULL ELSE CAST("5コースS0" AS INTEGER) END,
  CASE WHEN "5コースS1" = '' OR "5コースS1" IS NULL THEN NULL ELSE CAST("5コースS1" AS INTEGER) END,
  CASE WHEN "5コースS2" = '' OR "5コースS2" IS NULL THEN NULL ELSE CAST("5コースS2" AS INTEGER) END,
  CASE WHEN "6コース1着" = '' OR "6コース1着" IS NULL THEN NULL ELSE CAST("6コース1着" AS INTEGER) END,
  CASE WHEN "6コース2着" = '' OR "6コース2着" IS NULL THEN NULL ELSE CAST("6コース2着" AS INTEGER) END,
  CASE WHEN "6コース3着" = '' OR "6コース3着" IS NULL THEN NULL ELSE CAST("6コース3着" AS INTEGER) END,
  CASE WHEN "6コース4着" = '' OR "6コース4着" IS NULL THEN NULL ELSE CAST("6コース4着" AS INTEGER) END,
  CASE WHEN "6コース5着" = '' OR "6コース5着" IS NULL THEN NULL ELSE CAST("6コース5着" AS INTEGER) END,
  CASE WHEN "6コース6着" = '' OR "6コース6着" IS NULL THEN NULL ELSE CAST("6コース6着" AS INTEGER) END,
  CASE WHEN "6コースF" = '' OR "6コースF" IS NULL THEN NULL ELSE CAST("6コースF" AS INTEGER) END,
  CASE WHEN "6コースL0" = '' OR "6コースL0" IS NULL THEN NULL ELSE CAST("6コースL0" AS INTEGER) END,
  CASE WHEN "6コースL1" = '' OR "6コースL1" IS NULL THEN NULL ELSE CAST("6コースL1" AS INTEGER) END,
  CASE WHEN "6コースK0" = '' OR "6コースK0" IS NULL THEN NULL ELSE CAST("6コースK0" AS INTEGER) END,
  CASE WHEN "6コースK1" = '' OR "6コースK1" IS NULL THEN NULL ELSE CAST("6コースK1" AS INTEGER) END,
  CASE WHEN "6コースS0" = '' OR "6コースS0" IS NULL THEN NULL ELSE CAST("6コースS0" AS INTEGER) END,
  CASE WHEN "6コースS1" = '' OR "6コースS1" IS NULL THEN NULL ELSE CAST("6コースS1" AS INTEGER) END,
  CASE WHEN "6コースS2" = '' OR "6コースS2" IS NULL THEN NULL ELSE CAST("6コースS2" AS INTEGER) END,
  CASE WHEN コース無L0 = '' OR コース無L0 IS NULL THEN NULL ELSE CAST(コース無L0 AS INTEGER) END,
  CASE WHEN コース無L1 = '' OR コース無L1 IS NULL THEN NULL ELSE CAST(コース無L1 AS INTEGER) END,
  CASE WHEN コース無K0 = '' OR コース無K0 IS NULL THEN NULL ELSE CAST(コース無K0 AS INTEGER) END,
  CASE WHEN コース無K1 = '' OR コース無K1 IS NULL THEN NULL ELSE CAST(コース無K1 AS INTEGER) END,
  出身地
FROM temp_racers_incremental
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != ''
  AND NOT EXISTS (
    SELECT 1 FROM racers r
    WHERE r.year = CAST(temp_racers_incremental.年 AS INTEGER)
      AND r.period = temp_racers_incremental.期
      AND r.racer_number = CAST(temp_racers_incremental.登番 AS INTEGER)
  );

-- 一時テーブル削除
DROP TABLE temp_racers_incremental;
EOF

# 増分インポート結果の確認
NEW_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM racers;")
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
  year, period, racer_number, name_kanji, class
FROM racers 
ORDER BY year DESC, period DESC, racer_number DESC 
LIMIT 3;"

echo ""
echo "=== レーサー期別成績データ増分インポート完了 ==="
