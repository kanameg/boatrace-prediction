-- results テーブル定義
-- レース結果、払戻金、着順などの情報を格納

DROP TABLE IF EXISTS results;

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
  win_boat_number INTEGER,
  win_payout INTEGER,
  place_1st_boat_number INTEGER,
  place_1st_payout INTEGER,
  place_2nd_boat_number INTEGER,
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
  
  -- 1号艇結果
  racer1_finish_position INTEGER,
  racer1_number INTEGER,
  racer1_boat_number INTEGER,
  racer1_motor_number INTEGER,
  racer1_boat_number_assigned INTEGER,
  racer1_exhibition_time REAL,
  racer1_start_course INTEGER,
  racer1_start_timing REAL,
  racer1_race_time REAL,
  
  -- 2号艇結果
  racer2_finish_position INTEGER,
  racer2_number INTEGER,
  racer2_boat_number INTEGER,
  racer2_motor_number INTEGER,
  racer2_boat_number_assigned INTEGER,
  racer2_exhibition_time REAL,
  racer2_start_course INTEGER,
  racer2_start_timing REAL,
  racer2_race_time REAL,
  
  -- 3号艇結果
  racer3_finish_position INTEGER,
  racer3_number INTEGER,
  racer3_boat_number INTEGER,
  racer3_motor_number INTEGER,
  racer3_boat_number_assigned INTEGER,
  racer3_exhibition_time REAL,
  racer3_start_course INTEGER,
  racer3_start_timing REAL,
  racer3_race_time REAL,
  
  -- 4号艇結果
  racer4_finish_position INTEGER,
  racer4_number INTEGER,
  racer4_boat_number INTEGER,
  racer4_motor_number INTEGER,
  racer4_boat_number_assigned INTEGER,
  racer4_exhibition_time REAL,
  racer4_start_course INTEGER,
  racer4_start_timing REAL,
  racer4_race_time REAL,
  
  -- 5号艇結果
  racer5_finish_position INTEGER,
  racer5_number INTEGER,
  racer5_boat_number INTEGER,
  racer5_motor_number INTEGER,
  racer5_boat_number_assigned INTEGER,
  racer5_exhibition_time REAL,
  racer5_start_course INTEGER,
  racer5_start_timing REAL,
  racer5_race_time REAL,
  
  -- 6号艇結果
  racer6_finish_position INTEGER,
  racer6_number INTEGER,
  racer6_boat_number INTEGER,
  racer6_motor_number INTEGER,
  racer6_boat_number_assigned INTEGER,
  racer6_exhibition_time REAL,
  racer6_start_course INTEGER,
  racer6_start_timing REAL,
  racer6_race_time REAL,
  
  -- インデックス用の複合キー
  UNIQUE(year, month, day, venue_code, race_number)
);

-- インデックス作成
CREATE INDEX idx_results_date ON results(year, month, day);
CREATE INDEX idx_results_venue ON results(venue_code);
CREATE INDEX idx_results_race ON results(race_number);
CREATE INDEX idx_results_racer1 ON results(racer1_number);
CREATE INDEX idx_results_racer2 ON results(racer2_number);
CREATE INDEX idx_results_racer3 ON results(racer3_number);
CREATE INDEX idx_results_racer4 ON results(racer4_number);
CREATE INDEX idx_results_racer5 ON results(racer5_number);
CREATE INDEX idx_results_racer6 ON results(racer6_number);
