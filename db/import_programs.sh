#!/bin/bash
# data/programs.csvをSQLiteデータベースにインポートするスクリプト
# 新しい構造: 1艇1行のフォーマットに対応

# データベースファイル
DB_FILE="boat_race.db"
CSV_FILE="../data/programs.csv"
SQL_FILE="programs.sql"

echo "=== Programs CSVインポートスクリプト ==="
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

-- 一時テーブルから本テーブルにデータを移行
INSERT INTO programs (
  year, month, day, venue_code, race_number, distance_m, deadline_time,
  frame_number, racer_number, age, branch, weight, class,
  national_win_rate, national_quinella_rate, local_win_rate, local_quinella_rate,
  motor_number, motor_quinella_rate, boat_number, boat_quinella_rate
)
SELECT 
  CAST(年 AS INTEGER), CAST(月 AS INTEGER), CAST(日 AS INTEGER),
  CAST(レース場番号 AS INTEGER), CAST(レース番号 AS INTEGER), CAST(距離 AS INTEGER),
  投票締切時間,
  CAST(枠番 AS INTEGER), CAST(選手登番 AS INTEGER), CAST(年齢 AS INTEGER), 支部, CAST(体重 AS REAL), 級別,
  CAST(全国勝率 AS REAL), CAST(全国2連率 AS REAL), CAST(当地勝率 AS REAL), CAST(当地2連率 AS REAL),
  CAST(モーター番号 AS INTEGER), CAST(モーター2連率 AS REAL), CAST(ボート番号 AS INTEGER), CAST(ボート2連率 AS REAL)
FROM temp_programs
WHERE 年 != '年' AND 年 IS NOT NULL AND 年 != '';

-- 一時テーブルを削除
DROP TABLE temp_programs;
EOF

if [ $? -ne 0 ]; then
    echo "エラー: CSVインポートに失敗しました"
    exit 1
fi

# インポート結果確認
RECORD_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
echo "インポート完了: $RECORD_COUNT 件のレコードが追加されました"

echo "=== インポート完了 ==="
