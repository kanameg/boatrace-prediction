-- レース番組表テーブル作成用SQLスクリプト
-- data/programs.csvをインポートするためのテーブル定義
-- 新しい構造: 1艇1行のフォーマットに対応

-- 既存のテーブルを削除（存在する場合）
DROP TABLE IF EXISTS programs;

-- 一時インポート用テーブル（CSVと同じカラム名）
DROP TABLE IF EXISTS temp_programs;
CREATE TABLE temp_programs (
  年 INTEGER,
  月 INTEGER,
  日 INTEGER,
  レース場番号 INTEGER,
  レース番号 INTEGER,
  距離 INTEGER,
  投票締切時間 TEXT,
  枠番 INTEGER,
  選手登番 INTEGER,
  年齢 INTEGER,
  支部 TEXT,
  体重 REAL,
  級別 TEXT,
  全国勝率 REAL,
  全国2連率 REAL,
  当地勝率 REAL,
  当地2連率 REAL,
  モーター番号 INTEGER,
  モーター2連率 REAL,
  ボート番号 INTEGER,
  ボート2連率 REAL
);

-- 本テーブル（英語カラム名、正規化された構造）
CREATE TABLE programs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,
  day INTEGER NOT NULL,
  venue_code INTEGER NOT NULL,
  race_number INTEGER NOT NULL,
  distance_m INTEGER NOT NULL,
  deadline_time TEXT NOT NULL,
  
  -- 選手情報（1艇1行構造）
  frame_number INTEGER NOT NULL,
  racer_number INTEGER NOT NULL,
  age INTEGER NOT NULL,
  branch TEXT NOT NULL,
  weight REAL NOT NULL,
  class TEXT NOT NULL,
  national_win_rate REAL NOT NULL,
  national_quinella_rate REAL NOT NULL,
  local_win_rate REAL NOT NULL,
  local_quinella_rate REAL NOT NULL,
  motor_number INTEGER NOT NULL,
  motor_quinella_rate REAL NOT NULL,
  boat_number INTEGER NOT NULL,
  boat_quinella_rate REAL NOT NULL,
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  -- インデックス用の複合キー（年月日、会場、レース番号、選手登番でユニーク）
  UNIQUE(year, month, day, venue_code, race_number, racer_number)
);

-- インデックスの作成
CREATE INDEX idx_programs_date ON programs(year, month, day);
CREATE INDEX idx_programs_venue ON programs(venue_code);
CREATE INDEX idx_programs_race ON programs(race_number);
CREATE INDEX idx_programs_frame ON programs(frame_number);
CREATE INDEX idx_programs_racer ON programs(racer_number);
CREATE INDEX idx_programs_date_venue ON programs(year, month, day, venue_code);
CREATE INDEX idx_programs_date_venue_race ON programs(year, month, day, venue_code, race_number);
