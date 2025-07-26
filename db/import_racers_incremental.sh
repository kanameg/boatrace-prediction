#!/bin/bash
# data/racers.csvをSQLiteデータベースに増分インポートするスクリプト
# 既存データとの重複をチェックして新しいデータのみを追加

# データベースファイル
DB_FILE="boat_race.db"
CSV_FILE="../data/racers.csv"
SQL_FILE="racers.sql"

echo "=== Racers CSV増分インポートスクリプト ==="
echo "データベース: $DB_FILE"
echo "CSVファイル: $CSV_FILE"
echo "SQLファイル: $SQL_FILE"

# ファイル存在チェック
if [ ! -f "$CSV_FILE" ]; then
    echo "エラー: CSVファイルが見つかりません: $CSV_FILE"
    exit 1
fi

if [ ! -f "$DB_FILE" ]; then
    echo "エラー: データベースファイルが見つかりません: $DB_FILE"
    echo "まず import_racers.sh を実行してテーブルを作成してください"
    exit 1
fi

# テーブル存在チェック
TABLE_EXISTS=$(sqlite3 "$DB_FILE" "SELECT name FROM sqlite_master WHERE type='table' AND name='racers';" 2>/dev/null)
if [ -z "$TABLE_EXISTS" ]; then
    echo "racersテーブルが存在しません。テーブルを作成中..."
    if [ ! -f "$SQL_FILE" ]; then
        echo "エラー: SQLファイルが見つかりません: $SQL_FILE"
        exit 1
    fi
    sqlite3 "$DB_FILE" < "$SQL_FILE"
    if [ $? -ne 0 ]; then
        echo "エラー: テーブル作成に失敗しました"
        exit 1
    fi
fi

# インポート前のレコード数確認
BEFORE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM racers;")
echo "インポート前のレコード数: $BEFORE_COUNT"

# CSVデータを増分インポート
echo "CSVデータを増分インポート中..."
sqlite3 "$DB_FILE" <<EOF
.mode csv
.headers on
.import $CSV_FILE temp_racers

-- 既存データと重複しないデータのみを挿入（年、期、登番の組み合わせでチェック）
INSERT INTO racers (
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
  CASE WHEN \`1着回数\` = '' OR \`1着回数\` IS NULL THEN NULL ELSE CAST(\`1着回数\` AS INTEGER) END,
  CASE WHEN \`2着回数\` = '' OR \`2着回数\` IS NULL THEN NULL ELSE CAST(\`2着回数\` AS INTEGER) END,
  CASE WHEN 出走回数 = '' OR 出走回数 IS NULL THEN NULL ELSE CAST(出走回数 AS INTEGER) END,
  CASE WHEN 優出回数 = '' OR 優出回数 IS NULL THEN NULL ELSE CAST(優出回数 AS INTEGER) END,
  CASE WHEN 優勝回数 = '' OR 優勝回数 IS NULL THEN NULL ELSE CAST(優勝回数 AS INTEGER) END,
  CASE WHEN 平均スタートタイミング = '' OR 平均スタートタイミング IS NULL THEN NULL ELSE CAST(平均スタートタイミング AS REAL) END,
  CASE WHEN \`1コース進入回数\` = '' OR \`1コース進入回数\` IS NULL THEN NULL ELSE CAST(\`1コース進入回数\` AS INTEGER) END,
  CASE WHEN \`1コース複勝率\` = '' OR \`1コース複勝率\` IS NULL THEN NULL ELSE CAST(\`1コース複勝率\` AS REAL) END,
  CASE WHEN \`1コース平均スタートタイミング\` = '' OR \`1コース平均スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`1コース平均スタートタイミング\` AS REAL) END,
  CASE WHEN \`1コース平均スタート順位\` = '' OR \`1コース平均スタート順位\` IS NULL THEN NULL ELSE CAST(\`1コース平均スタート順位\` AS REAL) END,
  CASE WHEN \`2コース進入回数\` = '' OR \`2コース進入回数\` IS NULL THEN NULL ELSE CAST(\`2コース進入回数\` AS INTEGER) END,
  CASE WHEN \`2コース複勝率\` = '' OR \`2コース複勝率\` IS NULL THEN NULL ELSE CAST(\`2コース複勝率\` AS REAL) END,
  CASE WHEN \`2コース平均スタートタイミング\` = '' OR \`2コース平均スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`2コース平均スタートタイミング\` AS REAL) END,
  CASE WHEN \`2コース平均スタート順位\` = '' OR \`2コース平均スタート順位\` IS NULL THEN NULL ELSE CAST(\`2コース平均スタート順位\` AS REAL) END,
  CASE WHEN \`3コース進入回数\` = '' OR \`3コース進入回数\` IS NULL THEN NULL ELSE CAST(\`3コース進入回数\` AS INTEGER) END,
  CASE WHEN \`3コース複勝率\` = '' OR \`3コース複勝率\` IS NULL THEN NULL ELSE CAST(\`3コース複勝率\` AS REAL) END,
  CASE WHEN \`3コース平均スタートタイミング\` = '' OR \`3コース平均スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`3コース平均スタートタイミング\` AS REAL) END,
  CASE WHEN \`3コース平均スタート順位\` = '' OR \`3コース平均スタート順位\` IS NULL THEN NULL ELSE CAST(\`3コース平均スタート順位\` AS REAL) END,
  CASE WHEN \`4コース進入回数\` = '' OR \`4コース進入回数\` IS NULL THEN NULL ELSE CAST(\`4コース進入回数\` AS INTEGER) END,
  CASE WHEN \`4コース複勝率\` = '' OR \`4コース複勝率\` IS NULL THEN NULL ELSE CAST(\`4コース複勝率\` AS REAL) END,
  CASE WHEN \`4コース平均スタートタイミング\` = '' OR \`4コース平均スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`4コース平均スタートタイミング\` AS REAL) END,
  CASE WHEN \`4コース平均スタート順位\` = '' OR \`4コース平均スタート順位\` IS NULL THEN NULL ELSE CAST(\`4コース平均スタート順位\` AS REAL) END,
  CASE WHEN \`5コース進入回数\` = '' OR \`5コース進入回数\` IS NULL THEN NULL ELSE CAST(\`5コース進入回数\` AS INTEGER) END,
  CASE WHEN \`5コース複勝率\` = '' OR \`5コース複勝率\` IS NULL THEN NULL ELSE CAST(\`5コース複勝率\` AS REAL) END,
  CASE WHEN \`5コース平均スタートタイミング\` = '' OR \`5コース平均スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`5コース平均スタートタイミング\` AS REAL) END,
  CASE WHEN \`5コース平均スタート順位\` = '' OR \`5コース平均スタート順位\` IS NULL THEN NULL ELSE CAST(\`5コース平均スタート順位\` AS REAL) END,
  CASE WHEN \`6コース進入回数\` = '' OR \`6コース進入回数\` IS NULL THEN NULL ELSE CAST(\`6コース進入回数\` AS INTEGER) END,
  CASE WHEN \`6コース複勝率\` = '' OR \`6コース複勝率\` IS NULL THEN NULL ELSE CAST(\`6コース複勝率\` AS REAL) END,
  CASE WHEN \`6コース平均スタートタイミング\` = '' OR \`6コース平均スタートタイミング\` IS NULL THEN NULL ELSE CAST(\`6コース平均スタートタイミング\` AS REAL) END,
  CASE WHEN \`6コース平均スタート順位\` = '' OR \`6コース平均スタート順位\` IS NULL THEN NULL ELSE CAST(\`6コース平均スタート順位\` AS REAL) END,
  前期級, 前々期級, 前々々期級,
  CASE WHEN 前期能力指数 = '' OR 前期能力指数 IS NULL THEN NULL ELSE CAST(前期能力指数 AS REAL) END,
  CASE WHEN 今期能力指数 = '' OR 今期能力指数 IS NULL THEN NULL ELSE CAST(今期能力指数 AS REAL) END,
  算出期間自, 算出期間至,
  CASE WHEN 養成期 = '' OR 養成期 IS NULL THEN NULL ELSE CAST(養成期 AS INTEGER) END,
  CASE WHEN \`1コース1着回数\` = '' OR \`1コース1着回数\` IS NULL THEN NULL ELSE CAST(\`1コース1着回数\` AS INTEGER) END,
  CASE WHEN \`1コース2着回数\` = '' OR \`1コース2着回数\` IS NULL THEN NULL ELSE CAST(\`1コース2着回数\` AS INTEGER) END,
  CASE WHEN \`1コース3着回数\` = '' OR \`1コース3着回数\` IS NULL THEN NULL ELSE CAST(\`1コース3着回数\` AS INTEGER) END,
  CASE WHEN \`1コース4着回数\` = '' OR \`1コース4着回数\` IS NULL THEN NULL ELSE CAST(\`1コース4着回数\` AS INTEGER) END,
  CASE WHEN \`1コース5着回数\` = '' OR \`1コース5着回数\` IS NULL THEN NULL ELSE CAST(\`1コース5着回数\` AS INTEGER) END,
  CASE WHEN \`1コース6着回数\` = '' OR \`1コース6着回数\` IS NULL THEN NULL ELSE CAST(\`1コース6着回数\` AS INTEGER) END,
  CASE WHEN \`1コースF回数\` = '' OR \`1コースF回数\` IS NULL THEN NULL ELSE CAST(\`1コースF回数\` AS INTEGER) END,
  CASE WHEN \`1コースL0回数\` = '' OR \`1コースL0回数\` IS NULL THEN NULL ELSE CAST(\`1コースL0回数\` AS INTEGER) END,
  CASE WHEN \`1コースL1回数\` = '' OR \`1コースL1回数\` IS NULL THEN NULL ELSE CAST(\`1コースL1回数\` AS INTEGER) END,
  CASE WHEN \`1コースK0回数\` = '' OR \`1コースK0回数\` IS NULL THEN NULL ELSE CAST(\`1コースK0回数\` AS INTEGER) END,
  CASE WHEN \`1コースK1回数\` = '' OR \`1コースK1回数\` IS NULL THEN NULL ELSE CAST(\`1コースK1回数\` AS INTEGER) END,
  CASE WHEN \`1コースS0回数\` = '' OR \`1コースS0回数\` IS NULL THEN NULL ELSE CAST(\`1コースS0回数\` AS INTEGER) END,
  CASE WHEN \`1コースS1回数\` = '' OR \`1コースS1回数\` IS NULL THEN NULL ELSE CAST(\`1コースS1回数\` AS INTEGER) END,
  CASE WHEN \`1コースS2回数\` = '' OR \`1コースS2回数\` IS NULL THEN NULL ELSE CAST(\`1コースS2回数\` AS INTEGER) END,
  CASE WHEN \`2コース1着回数\` = '' OR \`2コース1着回数\` IS NULL THEN NULL ELSE CAST(\`2コース1着回数\` AS INTEGER) END,
  CASE WHEN \`2コース2着回数\` = '' OR \`2コース2着回数\` IS NULL THEN NULL ELSE CAST(\`2コース2着回数\` AS INTEGER) END,
  CASE WHEN \`2コース3着回数\` = '' OR \`2コース3着回数\` IS NULL THEN NULL ELSE CAST(\`2コース3着回数\` AS INTEGER) END,
  CASE WHEN \`2コース4着回数\` = '' OR \`2コース4着回数\` IS NULL THEN NULL ELSE CAST(\`2コース4着回数\` AS INTEGER) END,
  CASE WHEN \`2コース5着回数\` = '' OR \`2コース5着回数\` IS NULL THEN NULL ELSE CAST(\`2コース5着回数\` AS INTEGER) END,
  CASE WHEN \`2コース6着回数\` = '' OR \`2コース6着回数\` IS NULL THEN NULL ELSE CAST(\`2コース6着回数\` AS INTEGER) END,
  CASE WHEN \`2コースF回数\` = '' OR \`2コースF回数\` IS NULL THEN NULL ELSE CAST(\`2コースF回数\` AS INTEGER) END,
  CASE WHEN \`2コースL0回数\` = '' OR \`2コースL0回数\` IS NULL THEN NULL ELSE CAST(\`2コースL0回数\` AS INTEGER) END,
  CASE WHEN \`2コースL1回数\` = '' OR \`2コースL1回数\` IS NULL THEN NULL ELSE CAST(\`2コースL1回数\` AS INTEGER) END,
  CASE WHEN \`2コースK0回数\` = '' OR \`2コースK0回数\` IS NULL THEN NULL ELSE CAST(\`2コースK0回数\` AS INTEGER) END,
  CASE WHEN \`2コースK1回数\` = '' OR \`2コースK1回数\` IS NULL THEN NULL ELSE CAST(\`2コースK1回数\` AS INTEGER) END,
  CASE WHEN \`2コースS0回数\` = '' OR \`2コースS0回数\` IS NULL THEN NULL ELSE CAST(\`2コースS0回数\` AS INTEGER) END,
  CASE WHEN \`2コースS1回数\` = '' OR \`2コースS1回数\` IS NULL THEN NULL ELSE CAST(\`2コースS1回数\` AS INTEGER) END,
  CASE WHEN \`2コースS2回数\` = '' OR \`2コースS2回数\` IS NULL THEN NULL ELSE CAST(\`2コースS2回数\` AS INTEGER) END,
  CASE WHEN \`3コース1着回数\` = '' OR \`3コース1着回数\` IS NULL THEN NULL ELSE CAST(\`3コース1着回数\` AS INTEGER) END,
  CASE WHEN \`3コース2着回数\` = '' OR \`3コース2着回数\` IS NULL THEN NULL ELSE CAST(\`3コース2着回数\` AS INTEGER) END,
  CASE WHEN \`3コース3着回数\` = '' OR \`3コース3着回数\` IS NULL THEN NULL ELSE CAST(\`3コース3着回数\` AS INTEGER) END,
  CASE WHEN \`3コース4着回数\` = '' OR \`3コース4着回数\` IS NULL THEN NULL ELSE CAST(\`3コース4着回数\` AS INTEGER) END,
  CASE WHEN \`3コース5着回数\` = '' OR \`3コース5着回数\` IS NULL THEN NULL ELSE CAST(\`3コース5着回数\` AS INTEGER) END,
  CASE WHEN \`3コース6着回数\` = '' OR \`3コース6着回数\` IS NULL THEN NULL ELSE CAST(\`3コース6着回数\` AS INTEGER) END,
  CASE WHEN \`3コースF回数\` = '' OR \`3コースF回数\` IS NULL THEN NULL ELSE CAST(\`3コースF回数\` AS INTEGER) END,
  CASE WHEN \`3コースL0回数\` = '' OR \`3コースL0回数\` IS NULL THEN NULL ELSE CAST(\`3コースL0回数\` AS INTEGER) END,
  CASE WHEN \`3コースL1回数\` = '' OR \`3コースL1回数\` IS NULL THEN NULL ELSE CAST(\`3コースL1回数\` AS INTEGER) END,
  CASE WHEN \`3コースK0回数\` = '' OR \`3コースK0回数\` IS NULL THEN NULL ELSE CAST(\`3コースK0回数\` AS INTEGER) END,
  CASE WHEN \`3コースK1回数\` = '' OR \`3コースK1回数\` IS NULL THEN NULL ELSE CAST(\`3コースK1回数\` AS INTEGER) END,
  CASE WHEN \`3コースS0回数\` = '' OR \`3コースS0回数\` IS NULL THEN NULL ELSE CAST(\`3コースS0回数\` AS INTEGER) END,
  CASE WHEN \`3コースS1回数\` = '' OR \`3コースS1回数\` IS NULL THEN NULL ELSE CAST(\`3コースS1回数\` AS INTEGER) END,
  CASE WHEN \`3コースS2回数\` = '' OR \`3コースS2回数\` IS NULL THEN NULL ELSE CAST(\`3コースS2回数\` AS INTEGER) END,
  CASE WHEN \`4コース1着回数\` = '' OR \`4コース1着回数\` IS NULL THEN NULL ELSE CAST(\`4コース1着回数\` AS INTEGER) END,
  CASE WHEN \`4コース2着回数\` = '' OR \`4コース2着回数\` IS NULL THEN NULL ELSE CAST(\`4コース2着回数\` AS INTEGER) END,
  CASE WHEN \`4コース3着回数\` = '' OR \`4コース3着回数\` IS NULL THEN NULL ELSE CAST(\`4コース3着回数\` AS INTEGER) END,
  CASE WHEN \`4コース4着回数\` = '' OR \`4コース4着回数\` IS NULL THEN NULL ELSE CAST(\`4コース4着回数\` AS INTEGER) END,
  CASE WHEN \`4コース5着回数\` = '' OR \`4コース5着回数\` IS NULL THEN NULL ELSE CAST(\`4コース5着回数\` AS INTEGER) END,
  CASE WHEN \`4コース6着回数\` = '' OR \`4コース6着回数\` IS NULL THEN NULL ELSE CAST(\`4コース6着回数\` AS INTEGER) END,
  CASE WHEN \`4コースF回数\` = '' OR \`4コースF回数\` IS NULL THEN NULL ELSE CAST(\`4コースF回数\` AS INTEGER) END,
  CASE WHEN \`4コースL0回数\` = '' OR \`4コースL0回数\` IS NULL THEN NULL ELSE CAST(\`4コースL0回数\` AS INTEGER) END,
  CASE WHEN \`4コースL1回数\` = '' OR \`4コースL1回数\` IS NULL THEN NULL ELSE CAST(\`4コースL1回数\` AS INTEGER) END,
  CASE WHEN \`4コースK0回数\` = '' OR \`4コースK0回数\` IS NULL THEN NULL ELSE CAST(\`4コースK0回数\` AS INTEGER) END,
  CASE WHEN \`4コースK1回数\` = '' OR \`4コースK1回数\` IS NULL THEN NULL ELSE CAST(\`4コースK1回数\` AS INTEGER) END,
  CASE WHEN \`4コースS0回数\` = '' OR \`4コースS0回数\` IS NULL THEN NULL ELSE CAST(\`4コースS0回数\` AS INTEGER) END,
  CASE WHEN \`4コースS1回数\` = '' OR \`4コースS1回数\` IS NULL THEN NULL ELSE CAST(\`4コースS1回数\` AS INTEGER) END,
  CASE WHEN \`4コースS2回数\` = '' OR \`4コースS2回数\` IS NULL THEN NULL ELSE CAST(\`4コースS2回数\` AS INTEGER) END,
  CASE WHEN \`5コース1着回数\` = '' OR \`5コース1着回数\` IS NULL THEN NULL ELSE CAST(\`5コース1着回数\` AS INTEGER) END,
  CASE WHEN \`5コース2着回数\` = '' OR \`5コース2着回数\` IS NULL THEN NULL ELSE CAST(\`5コース2着回数\` AS INTEGER) END,
  CASE WHEN \`5コース3着回数\` = '' OR \`5コース3着回数\` IS NULL THEN NULL ELSE CAST(\`5コース3着回数\` AS INTEGER) END,
  CASE WHEN \`5コース4着回数\` = '' OR \`5コース4着回数\` IS NULL THEN NULL ELSE CAST(\`5コース4着回数\` AS INTEGER) END,
  CASE WHEN \`5コース5着回数\` = '' OR \`5コース5着回数\` IS NULL THEN NULL ELSE CAST(\`5コース5着回数\` AS INTEGER) END,
  CASE WHEN \`5コース6着回数\` = '' OR \`5コース6着回数\` IS NULL THEN NULL ELSE CAST(\`5コース6着回数\` AS INTEGER) END,
  CASE WHEN \`5コースF回数\` = '' OR \`5コースF回数\` IS NULL THEN NULL ELSE CAST(\`5コースF回数\` AS INTEGER) END,
  CASE WHEN \`5コースL0回数\` = '' OR \`5コースL0回数\` IS NULL THEN NULL ELSE CAST(\`5コースL0回数\` AS INTEGER) END,
  CASE WHEN \`5コースL1回数\` = '' OR \`5コースL1回数\` IS NULL THEN NULL ELSE CAST(\`5コースL1回数\` AS INTEGER) END,
  CASE WHEN \`5コースK0回数\` = '' OR \`5コースK0回数\` IS NULL THEN NULL ELSE CAST(\`5コースK0回数\` AS INTEGER) END,
  CASE WHEN \`5コースK1回数\` = '' OR \`5コースK1回数\` IS NULL THEN NULL ELSE CAST(\`5コースK1回数\` AS INTEGER) END,
  CASE WHEN \`5コースS0回数\` = '' OR \`5コースS0回数\` IS NULL THEN NULL ELSE CAST(\`5コースS0回数\` AS INTEGER) END,
  CASE WHEN \`5コースS1回数\` = '' OR \`5コースS1回数\` IS NULL THEN NULL ELSE CAST(\`5コースS1回数\` AS INTEGER) END,
  CASE WHEN \`5コースS2回数\` = '' OR \`5コースS2回数\` IS NULL THEN NULL ELSE CAST(\`5コースS2回数\` AS INTEGER) END,
  CASE WHEN \`6コース1着回数\` = '' OR \`6コース1着回数\` IS NULL THEN NULL ELSE CAST(\`6コース1着回数\` AS INTEGER) END,
  CASE WHEN \`6コース2着回数\` = '' OR \`6コース2着回数\` IS NULL THEN NULL ELSE CAST(\`6コース2着回数\` AS INTEGER) END,
  CASE WHEN \`6コース3着回数\` = '' OR \`6コース3着回数\` IS NULL THEN NULL ELSE CAST(\`6コース3着回数\` AS INTEGER) END,
  CASE WHEN \`6コース4着回数\` = '' OR \`6コース4着回数\` IS NULL THEN NULL ELSE CAST(\`6コース4着回数\` AS INTEGER) END,
  CASE WHEN \`6コース5着回数\` = '' OR \`6コース5着回数\` IS NULL THEN NULL ELSE CAST(\`6コース5着回数\` AS INTEGER) END,
  CASE WHEN \`6コース6着回数\` = '' OR \`6コース6着回数\` IS NULL THEN NULL ELSE CAST(\`6コース6着回数\` AS INTEGER) END,
  CASE WHEN \`6コースF回数\` = '' OR \`6コースF回数\` IS NULL THEN NULL ELSE CAST(\`6コースF回数\` AS INTEGER) END,
  CASE WHEN \`6コースL0回数\` = '' OR \`6コースL0回数\` IS NULL THEN NULL ELSE CAST(\`6コースL0回数\` AS INTEGER) END,
  CASE WHEN \`6コースL1回数\` = '' OR \`6コースL1回数\` IS NULL THEN NULL ELSE CAST(\`6コースL1回数\` AS INTEGER) END,
  CASE WHEN \`6コースK0回数\` = '' OR \`6コースK0回数\` IS NULL THEN NULL ELSE CAST(\`6コースK0回数\` AS INTEGER) END,
  CASE WHEN \`6コースK1回数\` = '' OR \`6コースK1回数\` IS NULL THEN NULL ELSE CAST(\`6コースK1回数\` AS INTEGER) END,
  CASE WHEN \`6コースS0回数\` = '' OR \`6コースS0回数\` IS NULL THEN NULL ELSE CAST(\`6コースS0回数\` AS INTEGER) END,
  CASE WHEN \`6コースS1回数\` = '' OR \`6コースS1回数\` IS NULL THEN NULL ELSE CAST(\`6コースS1回数\` AS INTEGER) END,
  CASE WHEN \`6コースS2回数\` = '' OR \`6コースS2回数\` IS NULL THEN NULL ELSE CAST(\`6コースS2回数\` AS INTEGER) END,
  CASE WHEN \`コースなしL0回数\` = '' OR \`コースなしL0回数\` IS NULL THEN NULL ELSE CAST(\`コースなしL0回数\` AS INTEGER) END,
  CASE WHEN \`コースなしL1回数\` = '' OR \`コースなしL1回数\` IS NULL THEN NULL ELSE CAST(\`コースなしL1回数\` AS INTEGER) END,
  CASE WHEN \`コースなしK0回数\` = '' OR \`コースなしK0回数\` IS NULL THEN NULL ELSE CAST(\`コースなしK0回数\` AS INTEGER) END,
  CASE WHEN \`コースなしK1回数\` = '' OR \`コースなしK1回数\` IS NULL THEN NULL ELSE CAST(\`コースなしK1回数\` AS INTEGER) END,
  出身地
FROM temp_racers
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != ''
  AND NOT EXISTS (
    SELECT 1 FROM racers 
    WHERE racers.year = CAST(temp_racers.年 AS INTEGER) 
      AND racers.period = temp_racers.期 
      AND racers.racer_number = CAST(temp_racers.登番 AS INTEGER)
  );

-- 一時テーブルを削除
DROP TABLE temp_racers;
EOF

if [ $? -ne 0 ]; then
    echo "エラー: CSVインポートに失敗しました"
    exit 1
fi

# インポート結果確認
AFTER_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM racers;")
NEW_RECORDS=$((AFTER_COUNT - BEFORE_COUNT))
echo "インポート完了: $NEW_RECORDS 件の新しいレコードが追加されました"
echo "総レコード数: $AFTER_COUNT"

echo "=== 増分インポート完了 ==="
