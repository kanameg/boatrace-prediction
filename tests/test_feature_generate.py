import argparse
import unittest
from datetime import datetime

import numpy as np
import pandas as pd

# テスト対象のモジュールをインポート
from feature_generate import (
    calculate_course_win_rate_diff,
    calculate_national_win_rate_diff,
    make_race_id,
    validate_date_format,
)


class TestFeatureGenerate(unittest.TestCase):

    def test_make_race_id(self):
        """
        make_race_id関数のテスト
        """
        row = {"年": 2025, "月": 8, "日": 10, "レース場番号": 24, "レース番号": 12}
        expected_id = 202508102412
        self.assertEqual(make_race_id(row), expected_id)

    def test_validate_date_format(self):
        """
        validate_date_format関数のテスト
        """
        # 正常なケース
        self.assertEqual(validate_date_format("2025-01-01"), "2025-01-01")
        self.assertEqual(validate_date_format("2024-2-29"), "2024-2-29")
        # 異常なケース
        with self.assertRaises(argparse.ArgumentTypeError):
            validate_date_format("2025/01/01")  # スラッシュ区切りは許容しない
        with self.assertRaises(argparse.ArgumentTypeError):
            validate_date_format("2025-02-29")  # 存在しない日付（閏年でない）
        with self.assertRaises(argparse.ArgumentTypeError):
            validate_date_format("2025-04-31")  # 存在しない日付（4月は30日まで）
        # with self.assertRaises(argparse.ArgumentTypeError):
        #     validate_date_format("2025-1-1")
        with self.assertRaises(argparse.ArgumentTypeError):
            validate_date_format("invalid-date")  # 無効な日付形式

    def test_calculate_national_win_rate_diff(self):
        """
        calculate_national_win_rate_diff関数のテスト
        """
        programs_data = {
            "年": [2025, 2025, 2025, 2025],
            "月": [1, 1, 1, 1],
            "日": [1, 1, 1, 1],
            "レース場番号": [1, 1, 2, 2],
            "レース番号": [1, 1, 1, 1],
            "枠番": [1, 2, 1, 2],
            "選手登番": [1001, 1002, 1003, 1004],
            "全国勝率": [5.0, 7.0, 8.0, 4.0],
        }
        programs_df = pd.DataFrame(programs_data)

        # レースID 202501010101 の平均勝率: (5.0 + 7.0) / 2 = 6.0
        # 差分: 5.0 - 6.0 = -1.0, 7.0 - 6.0 = 1.0
        # レースID 202501010201 の平均勝率: (8.0 + 4.0) / 2 = 6.0
        # 差分: 8.0 - 6.0 = 2.0, 4.0 - 6.0 = -2.0

        result_df = calculate_national_win_rate_diff(programs_df)

        self.assertIn("レース内全国勝率差", result_df.columns)
        self.assertAlmostEqual(result_df.iloc[0]["レース内全国勝率差"], -1.0)
        self.assertAlmostEqual(result_df.iloc[1]["レース内全国勝率差"], 1.0)
        self.assertAlmostEqual(result_df.iloc[2]["レース内全国勝率差"], 2.0)
        self.assertAlmostEqual(result_df.iloc[3]["レース内全国勝率差"], -2.0)

    def test_calculate_course_win_rate_diff(self):
        """
        calculate_course_win_rate_diff関数のテスト
        """
        programs_data = {
            "年": [2025, 2025, 2025, 2025],
            "月": [1, 1, 1, 1],
            "日": [1, 1, 1, 1],
            "レース場番号": [1, 1, 1, 1],
            "レース番号": [1, 1, 1, 1],
            "枠番": [1, 2, 3, 4],
            "選手登番": [1001, 1002, 1003, 1004],
        }
        programs_df = pd.DataFrame(programs_data)

        racers_data = {
            "登番": [1001, 1002, 1003],
            "1コース1着回数": [10, 0, 5],
            "1コース進入回数": [100, 10, 20],
            "2コース1着回数": [5, 20, 0],
            "2コース進入回数": [50, 80, 10],
            "3コース1着回数": [0, 5, 10],
            "3コース進入回数": [20, 20, 40],
            "4コース1着回数": [0, 0, 0],
            "4コース進入回数": [0, 0, 0],  # 選手1004はデータなし
        }
        racers_df = pd.DataFrame(racers_data)

        # 1枠(1コース) 選手1001: 10/100 = 0.1
        # 2枠(2コース) 選手1002: 20/80 = 0.25
        # 3枠(3コース) 選手1003: 10/40 = 0.25
        # 4枠(4コース) 選手1004: データなし -> np.nan
        # 平均: (0.1 + 0.25 + 0.25) / 3 = 0.2
        # 差分:
        # 0.1 - 0.2 = -0.1
        # 0.25 - 0.2 = 0.05
        # 0.25 - 0.2 = 0.05
        # np.nan - 0.2 = np.nan

        result_df = calculate_course_win_rate_diff(programs_df, racers_df)

        self.assertIn("レース内コース別1着率差", result_df.columns)
        self.assertAlmostEqual(result_df.iloc[0]["レース内コース別1着率差"], -0.1)
        self.assertAlmostEqual(result_df.iloc[1]["レース内コース別1着率差"], 0.05)
        self.assertAlmostEqual(result_df.iloc[2]["レース内コース別1着率差"], 0.05)
        self.assertTrue(pd.isna(result_df.iloc[3]["レース内コース別1着率差"]))


if __name__ == "__main__":
    unittest.main()
