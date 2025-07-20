-- レーサー期別成績テーブル作成用SQLスクリプト
-- data/racers.csvをインポートするためのテーブル定義

-- 既存のテーブルを削除（存在する場合）
DROP TABLE IF EXISTS racers;

CREATE TABLE racers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  year INTEGER NOT NULL,
  period TEXT NOT NULL,
  racer_number INTEGER NOT NULL,
  name_kanji TEXT NOT NULL,
  name_kana TEXT NOT NULL,
  branch TEXT NOT NULL,
  class TEXT NOT NULL,
  year_name TEXT,
  birth_date TEXT,
  gender INTEGER,
  age INTEGER,
  height INTEGER,
  weight INTEGER,
  blood_type TEXT,
  win_rate REAL,
  quinella_rate REAL,
  first_place_count INTEGER,
  second_place_count INTEGER,
  total_races INTEGER,
  excellent_race_count INTEGER,
  victory_count INTEGER,
  avg_start_timing REAL,
  
  -- 1コース成績
  course1_entries INTEGER,
  course1_quinella_rate REAL,
  course1_avg_start_timing REAL,
  course1_avg_start_order REAL,
  
  -- 2コース成績
  course2_entries INTEGER,
  course2_quinella_rate REAL,
  course2_avg_start_timing REAL,
  course2_avg_start_order REAL,
  
  -- 3コース成績
  course3_entries INTEGER,
  course3_quinella_rate REAL,
  course3_avg_start_timing REAL,
  course3_avg_start_order REAL,
  
  -- 4コース成績
  course4_entries INTEGER,
  course4_quinella_rate REAL,
  course4_avg_start_timing REAL,
  course4_avg_start_order REAL,
  
  -- 5コース成績
  course5_entries INTEGER,
  course5_quinella_rate REAL,
  course5_avg_start_timing REAL,
  course5_avg_start_order REAL,
  
  -- 6コース成績
  course6_entries INTEGER,
  course6_quinella_rate REAL,
  course6_avg_start_timing REAL,
  course6_avg_start_order REAL,
  
  -- 級別履歴
  previous_class TEXT,
  previous_previous_class TEXT,
  previous_previous_previous_class TEXT,
  previous_ability_index REAL,
  current_ability_index REAL,
  
  -- 算出期間
  calculation_year INTEGER,
  calculation_period TEXT,
  calculation_start_date TEXT,
  calculation_end_date TEXT,
  training_period INTEGER,
  
  -- 1コース詳細成績
  course1_1st INTEGER, course1_2nd INTEGER, course1_3rd INTEGER,
  course1_4th INTEGER, course1_5th INTEGER, course1_6th INTEGER,
  course1_f INTEGER, course1_l0 INTEGER, course1_l1 INTEGER,
  course1_k0 INTEGER, course1_k1 INTEGER, course1_s0 INTEGER,
  course1_s1 INTEGER, course1_s2 INTEGER,
  
  -- 2コース詳細成績
  course2_1st INTEGER, course2_2nd INTEGER, course2_3rd INTEGER,
  course2_4th INTEGER, course2_5th INTEGER, course2_6th INTEGER,
  course2_f INTEGER, course2_l0 INTEGER, course2_l1 INTEGER,
  course2_k0 INTEGER, course2_k1 INTEGER, course2_s0 INTEGER,
  course2_s1 INTEGER, course2_s2 INTEGER,
  
  -- 3コース詳細成績
  course3_1st INTEGER, course3_2nd INTEGER, course3_3rd INTEGER,
  course3_4th INTEGER, course3_5th INTEGER, course3_6th INTEGER,
  course3_f INTEGER, course3_l0 INTEGER, course3_l1 INTEGER,
  course3_k0 INTEGER, course3_k1 INTEGER, course3_s0 INTEGER,
  course3_s1 INTEGER, course3_s2 INTEGER,
  
  -- 4コース詳細成績
  course4_1st INTEGER, course4_2nd INTEGER, course4_3rd INTEGER,
  course4_4th INTEGER, course4_5th INTEGER, course4_6th INTEGER,
  course4_f INTEGER, course4_l0 INTEGER, course4_l1 INTEGER,
  course4_k0 INTEGER, course4_k1 INTEGER, course4_s0 INTEGER,
  course4_s1 INTEGER, course4_s2 INTEGER,
  
  -- 5コース詳細成績
  course5_1st INTEGER, course5_2nd INTEGER, course5_3rd INTEGER,
  course5_4th INTEGER, course5_5th INTEGER, course5_6th INTEGER,
  course5_f INTEGER, course5_l0 INTEGER, course5_l1 INTEGER,
  course5_k0 INTEGER, course5_k1 INTEGER, course5_s0 INTEGER,
  course5_s1 INTEGER, course5_s2 INTEGER,
  
  -- 6コース詳細成績
  course6_1st INTEGER, course6_2nd INTEGER, course6_3rd INTEGER,
  course6_4th INTEGER, course6_5th INTEGER, course6_6th INTEGER,
  course6_f INTEGER, course6_l0 INTEGER, course6_l1 INTEGER,
  course6_k0 INTEGER, course6_k1 INTEGER, course6_s0 INTEGER,
  course6_s1 INTEGER, course6_s2 INTEGER,
  
  -- その他
  no_course_l0 INTEGER,
  no_course_l1 INTEGER,
  no_course_k0 INTEGER,
  no_course_k1 INTEGER,
  birthplace TEXT,
  
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  -- 複合インデックス
  UNIQUE(year, period, racer_number)
);

-- インデックス作成
CREATE INDEX idx_racers_racer_number ON racers(racer_number);
CREATE INDEX idx_racers_year_period ON racers(year, period);
CREATE INDEX idx_racers_class ON racers(class);
CREATE INDEX idx_racers_branch ON racers(branch);
