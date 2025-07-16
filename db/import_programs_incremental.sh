#!/bin/bash
# 増分でprograms.csvをインポートするスクリプト

DB_FILE="boat_race.db"
CSV_FILE="../data/programs.csv"

echo "=== Programs 増分インポートスクリプト ==="

# 現在のデータベースの最新日付を取得
LATEST_DATE=$(sqlite3 "$DB_FILE" "SELECT MAX(year || '-' || printf('%02d', month) || '-' || printf('%02d', day)) FROM programs;" 2>/dev/null)

if [ -z "$LATEST_DATE" ]; then
    echo "データベースが空です。完全インポートを実行してください。"
    exit 1
fi

echo "データベース内の最新日付: $LATEST_DATE"

# 一時テーブルを作成してCSVをインポート
sqlite3 "$DB_FILE" <<EOF
-- 一時テーブル作成
DROP TABLE IF EXISTS temp_new_programs;
CREATE TABLE temp_new_programs (
  年 TEXT,
  月 TEXT,
  日 TEXT,
  レース場番号 TEXT,
  レース番号 TEXT,
  距離 TEXT,
  投票締切時間 TEXT,
  '1艇_選手登番' TEXT,
  '1艇_年齢' TEXT,
  '1艇_支部' TEXT,
  '1艇_体重' TEXT,
  '1艇_級別' TEXT,
  '1艇_全国勝率' TEXT,
  '1艇_全国2連率' TEXT,
  '1艇_当地勝率' TEXT,
  '1艇_当地2連率' TEXT,
  '1艇_モーター番号' TEXT,
  '1艇_モーター2連率' TEXT,
  '1艇_ボート番号' TEXT,
  '1艇_ボート2連率' TEXT,
  '2艇_選手登番' TEXT,
  '2艇_年齢' TEXT,
  '2艇_支部' TEXT,
  '2艇_体重' TEXT,
  '2艇_級別' TEXT,
  '2艇_全国勝率' TEXT,
  '2艇_全国2連率' TEXT,
  '2艇_当地勝率' TEXT,
  '2艇_当地2連率' TEXT,
  '2艇_モーター番号' TEXT,
  '2艇_モーター2連率' TEXT,
  '2艇_ボート番号' TEXT,
  '2艇_ボート2連率' TEXT,
  '3艇_選手登番' TEXT,
  '3艇_年齢' TEXT,
  '3艇_支部' TEXT,
  '3艇_体重' TEXT,
  '3艇_級別' TEXT,
  '3艇_全国勝率' TEXT,
  '3艇_全国2連率' TEXT,
  '3艇_当地勝率' TEXT,
  '3艇_当地2連率' TEXT,
  '3艇_モーター番号' TEXT,
  '3艇_モーター2連率' TEXT,
  '3艇_ボート番号' TEXT,
  '3艇_ボート2連率' TEXT,
  '4艇_選手登番' TEXT,
  '4艇_年齢' TEXT,
  '4艇_支部' TEXT,
  '4艇_体重' TEXT,
  '4艇_級別' TEXT,
  '4艇_全国勝率' TEXT,
  '4艇_全国2連率' TEXT,
  '4艇_当地勝率' TEXT,
  '4艇_当地2連率' TEXT,
  '4艇_モーター番号' TEXT,
  '4艇_モーター2連率' TEXT,
  '4艇_ボート番号' TEXT,
  '4艇_ボート2連率' TEXT,
  '5艇_選手登番' TEXT,
  '5艇_年齢' TEXT,
  '5艇_支部' TEXT,
  '5艇_体重' TEXT,
  '5艇_級別' TEXT,
  '5艇_全国勝率' TEXT,
  '5艇_全国2連率' TEXT,
  '5艇_当地勝率' TEXT,
  '5艇_当地2連率' TEXT,
  '5艇_モーター番号' TEXT,
  '5艇_モーター2連率' TEXT,
  '5艇_ボート番号' TEXT,
  '5艇_ボート2連率' TEXT,
  '6艇_選手登番' TEXT,
  '6艇_年齢' TEXT,
  '6艇_支部' TEXT,
  '6艇_体重' TEXT,
  '6艇_級別' TEXT,
  '6艇_全国勝率' TEXT,
  '6艇_全国2連率' TEXT,
  '6艇_当地勝率' TEXT,
  '6艇_当地2連率' TEXT,
  '6艇_モーター番号' TEXT,
  '6艇_モーター2連率' TEXT,
  '6艇_ボート番号' TEXT,
  '6艇_ボート2連率' TEXT
);

.mode csv
.headers off
.import $CSV_FILE temp_new_programs

-- 新しいデータのみを抽出して追加
INSERT OR IGNORE INTO programs (
  year, month, day, venue_code, race_number, distance_m, deadline_time,
  racer1_number, racer1_age, racer1_branch, racer1_weight, racer1_class, 
  racer1_national_win_rate, racer1_national_quinella_rate, racer1_local_win_rate, racer1_local_quinella_rate,
  racer1_motor_number, racer1_motor_quinella_rate, racer1_boat_number, racer1_boat_quinella_rate,
  racer2_number, racer2_age, racer2_branch, racer2_weight, racer2_class,
  racer2_national_win_rate, racer2_national_quinella_rate, racer2_local_win_rate, racer2_local_quinella_rate,
  racer2_motor_number, racer2_motor_quinella_rate, racer2_boat_number, racer2_boat_quinella_rate,
  racer3_number, racer3_age, racer3_branch, racer3_weight, racer3_class,
  racer3_national_win_rate, racer3_national_quinella_rate, racer3_local_win_rate, racer3_local_quinella_rate,
  racer3_motor_number, racer3_motor_quinella_rate, racer3_boat_number, racer3_boat_quinella_rate,
  racer4_number, racer4_age, racer4_branch, racer4_weight, racer4_class,
  racer4_national_win_rate, racer4_national_quinella_rate, racer4_local_win_rate, racer4_local_quinella_rate,
  racer4_motor_number, racer4_motor_quinella_rate, racer4_boat_number, racer4_boat_quinella_rate,
  racer5_number, racer5_age, racer5_branch, racer5_weight, racer5_class,
  racer5_national_win_rate, racer5_national_quinella_rate, racer5_local_win_rate, racer5_local_quinella_rate,
  racer5_motor_number, racer5_motor_quinella_rate, racer5_boat_number, racer5_boat_quinella_rate,
  racer6_number, racer6_age, racer6_branch, racer6_weight, racer6_class,
  racer6_national_win_rate, racer6_national_quinella_rate, racer6_local_win_rate, racer6_local_quinella_rate,
  racer6_motor_number, racer6_motor_quinella_rate, racer6_boat_number, racer6_boat_quinella_rate
)
SELECT 
  CAST(年 AS INTEGER), CAST(月 AS INTEGER), CAST(日 AS INTEGER), 
  CAST(レース場番号 AS INTEGER), CAST(レース番号 AS INTEGER), CAST(距離 AS INTEGER), 投票締切時間,
  CAST(\`1艇_選手登番\` AS INTEGER), CAST(\`1艇_年齢\` AS INTEGER), \`1艇_支部\`, CAST(\`1艇_体重\` AS REAL), \`1艇_級別\`,
  CAST(\`1艇_全国勝率\` AS REAL), CAST(\`1艇_全国2連率\` AS REAL), CAST(\`1艇_当地勝率\` AS REAL), CAST(\`1艇_当地2連率\` AS REAL),
  CAST(\`1艇_モーター番号\` AS INTEGER), CAST(\`1艇_モーター2連率\` AS REAL), CAST(\`1艇_ボート番号\` AS INTEGER), CAST(\`1艇_ボート2連率\` AS REAL),
  CAST(\`2艇_選手登番\` AS INTEGER), CAST(\`2艇_年齢\` AS INTEGER), \`2艇_支部\`, CAST(\`2艇_体重\` AS REAL), \`2艇_級別\`,
  CAST(\`2艇_全国勝率\` AS REAL), CAST(\`2艇_全国2連率\` AS REAL), CAST(\`2艇_当地勝率\` AS REAL), CAST(\`2艇_当地2連率\` AS REAL),
  CAST(\`2艇_モーター番号\` AS INTEGER), CAST(\`2艇_モーター2連率\` AS REAL), CAST(\`2艇_ボート番号\` AS INTEGER), CAST(\`2艇_ボート2連率\` AS REAL),
  CAST(\`3艇_選手登番\` AS INTEGER), CAST(\`3艇_年齢\` AS INTEGER), \`3艇_支部\`, CAST(\`3艇_体重\` AS REAL), \`3艇_級別\`,
  CAST(\`3艇_全国勝率\` AS REAL), CAST(\`3艇_全国2連率\` AS REAL), CAST(\`3艇_当地勝率\` AS REAL), CAST(\`3艇_当地2連率\` AS REAL),
  CAST(\`3艇_モーター番号\` AS INTEGER), CAST(\`3艇_モーター2連率\` AS REAL), CAST(\`3艇_ボート番号\` AS INTEGER), CAST(\`3艇_ボート2連率\` AS REAL),
  CAST(\`4艇_選手登番\` AS INTEGER), CAST(\`4艇_年齢\` AS INTEGER), \`4艇_支部\`, CAST(\`4艇_体重\` AS REAL), \`4艇_級別\`,
  CAST(\`4艇_全国勝率\` AS REAL), CAST(\`4艇_全国2連率\` AS REAL), CAST(\`4艇_当地勝率\` AS REAL), CAST(\`4艇_当地2連率\` AS REAL),
  CAST(\`4艇_モーター番号\` AS INTEGER), CAST(\`4艇_モーター2連率\` AS REAL), CAST(\`4艇_ボート番号\` AS INTEGER), CAST(\`4艇_ボート2連率\` AS REAL),
  CAST(\`5艇_選手登番\` AS INTEGER), CAST(\`5艇_年齢\` AS INTEGER), \`5艇_支部\`, CAST(\`5艇_体重\` AS REAL), \`5艇_級別\`,
  CAST(\`5艇_全国勝率\` AS REAL), CAST(\`5艇_全国2連率\` AS REAL), CAST(\`5艇_当地勝率\` AS REAL), CAST(\`5艇_当地2連率\` AS REAL),
  CAST(\`5艇_モーター番号\` AS INTEGER), CAST(\`5艇_モーター2連率\` AS REAL), CAST(\`5艇_ボート番号\` AS INTEGER), CAST(\`5艇_ボート2連率\` AS REAL),
  CAST(\`6艇_選手登番\` AS INTEGER), CAST(\`6艇_年齢\` AS INTEGER), \`6艇_支部\`, CAST(\`6艇_体重\` AS REAL), \`6艇_級別\`,
  CAST(\`6艇_全国勝率\` AS REAL), CAST(\`6艇_全国2連率\` AS REAL), CAST(\`6艇_当地勝率\` AS REAL), CAST(\`6艇_当地2連率\` AS REAL),
  CAST(\`6艇_モーター番号\` AS INTEGER), CAST(\`6艇_モーター2連率\` AS REAL), CAST(\`6艇_ボート番号\` AS INTEGER), CAST(\`6艇_ボート2連率\` AS REAL)
FROM temp_new_programs
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != '';

-- 一時テーブルを削除
DROP TABLE temp_new_programs;
EOF

# インポート結果確認
NEW_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
echo "更新完了: 現在のレコード数 $NEW_COUNT 件"

echo "=== 増分インポート完了 ==="
