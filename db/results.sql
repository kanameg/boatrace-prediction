-- レース結果テーブル作成用SQLスクリプト
-- data/results.csvをインポートするためのテーブル定義
-- 新しい構造: 1艇1行のフォーマットに対応

-- 既存のテーブルを削除（存在する場合）
DROP TABLE IF EXISTS results;

-- 一時インポート用テーブル（CSVと同じカラム名）
DROP TABLE IF EXISTS temp_results;
CREATE TABLE temp_results (
  年 INTEGER,
  月 INTEGER,
  日 INTEGER,
  レース場番号 INTEGER,
  レース番号 INTEGER,
  距離 INTEGER,
  天候 TEXT,
  風向 TEXT,
  風速 REAL,
  波高 REAL,
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
  着順 TEXT,
  選手登番 TEXT,
  艇番 TEXT,
  モーター番号 TEXT,
  ボート番号 TEXT,
  展示 TEXT,
  進入 TEXT,
  スタートタイミング TEXT,
  レースタイム TEXT
);

-- 本テーブル（英語カラム名、正規化された構造）
CREATE TABLE results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,
  day INTEGER NOT NULL,
  venue_code INTEGER NOT NULL,
  race_number INTEGER NOT NULL,
  
  -- レース条件
  distance INTEGER NOT NULL,
  weather TEXT NOT NULL,
  wind_direction TEXT NOT NULL,
  wind_speed REAL NOT NULL,
  wave_height REAL NOT NULL,
  
  -- 払戻金情報
  win_boat_number TEXT,
  win_payout INTEGER,
  place_1st_boat_number TEXT,
  place_1st_payout INTEGER,
  place_2nd_boat_number TEXT,
  place_2nd_payout INTEGER,
  
  -- 2連単
  exacta_boat_numbers TEXT,
  exacta_payout INTEGER,
  exacta_popularity INTEGER,
  
  -- 2連複
  quinella_boat_numbers TEXT,
  quinella_payout INTEGER,
  quinella_popularity INTEGER,
  
  -- 拡連複
  wide_1_boat_numbers TEXT,
  wide_1_payout INTEGER,
  wide_1_popularity INTEGER,
  wide_2_boat_numbers TEXT,
  wide_2_payout INTEGER,
  wide_2_popularity INTEGER,
  wide_3_boat_numbers TEXT,
  wide_3_payout INTEGER,
  wide_3_popularity INTEGER,
  
  -- 3連単
  trifecta_boat_numbers TEXT,
  trifecta_payout INTEGER,
  trifecta_popularity INTEGER,
  
  -- 3連複
  trio_boat_numbers TEXT,
  trio_payout INTEGER,
  trio_popularity INTEGER,
  
  -- 選手個別情報（1艇1行構造）
  finish_position INTEGER,
  racer_number INTEGER NOT NULL,
  boat_number INTEGER NOT NULL,
  motor_number INTEGER,
  boat_number_assigned INTEGER,
  exhibition_time REAL,
  start_course INTEGER,
  start_timing REAL,
  race_time TEXT,
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  -- インデックス用の複合キー（年月日、会場、レース番号、選手登番でユニーク）
  UNIQUE(year, month, day, venue_code, race_number, racer_number)
);

-- インデックスの作成
CREATE INDEX idx_results_date ON results(year, month, day);
CREATE INDEX idx_results_venue ON results(venue_code);
CREATE INDEX idx_results_race ON results(race_number);
CREATE INDEX idx_results_racer ON results(racer_number);
CREATE INDEX idx_results_finish ON results(finish_position);
CREATE INDEX idx_results_date_venue ON results(year, month, day, venue_code);
CREATE INDEX idx_results_date_venue_race ON results(year, month, day, venue_code, race_number);
