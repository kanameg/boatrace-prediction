#!/bin/bash
# data/programs.csvをSQLiteデータベースに増分インポートするスクリプト
# 既存データとの重複をチェックして新しいデータのみを追加
# 新しい構造: 1艇1行のフォーマットに対応

# データベースファイル
DB_FILE="boat_race.db"
CSV_FILE="../data/programs.csv"
SQL_FILE="programs.sql"

echo "=== Programs CSV増分インポートスクリプト ==="
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
    echo "まず import_programs.sh を実行してテーブルを作成してください"
    exit 1
fi

# テーブル存在チェック
TABLE_EXISTS=$(sqlite3 "$DB_FILE" "SELECT name FROM sqlite_master WHERE type='table' AND name='programs';" 2>/dev/null)
if [ -z "$TABLE_EXISTS" ]; then
    echo "programsテーブルが存在しません。テーブルを作成中..."
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
BEFORE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
echo "インポート前のレコード数: $BEFORE_COUNT"

# CSVデータを増分インポート
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
  racer_number, age, branch, weight, class,
  national_win_rate, national_quinella_rate, local_win_rate, local_quinella_rate,
  motor_number, motor_quinella_rate, boat_number, boat_quinella_rate
)
SELECT 
  CAST(年 AS INTEGER), CAST(月 AS INTEGER), CAST(日 AS INTEGER),
  CAST(レース場番号 AS INTEGER), CAST(レース番号 AS INTEGER), CAST(距離 AS INTEGER),
  投票締切時間,
  CAST(選手登番 AS INTEGER), CAST(年齢 AS INTEGER), 支部, CAST(体重 AS REAL), 級別,
  CAST(全国勝率 AS REAL), CAST(全国2連率 AS REAL), CAST(当地勝率 AS REAL), CAST(当地2連率 AS REAL),
  CAST(モーター番号 AS INTEGER), CAST(モーター2連率 AS REAL), CAST(ボート番号 AS INTEGER), CAST(ボート2連率 AS REAL)
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

# インポート結果確認
AFTER_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM programs;")
NEW_RECORDS=$((AFTER_COUNT - BEFORE_COUNT))
echo "インポート完了: $NEW_RECORDS 件の新しいレコードが追加されました"
echo "総レコード数: $AFTER_COUNT"

echo "=== 増分インポート完了 ==="
