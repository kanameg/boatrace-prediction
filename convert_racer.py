#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
レーサー期別成績変換プログラム
入力: racer_{YYYY}{e|l}.txt
出力: racer_{YYYY}{e|l}.csv
"""

import csv
import os
import re
import sys
import unicodedata


def get_char_width(char):
    """文字幅を取得（SHIFT-JISベース：全角文字は2、半角文字は1）"""
    code = ord(char)

    # ASCII文字（0x00-0x7F）: 1バイト
    if code <= 0x7F:
        return 1

    # 半角カタカナ（0xFF61-0xFF9F）: 1バイト
    if 0xFF61 <= code <= 0xFF9F:
        return 1

    # その他のUnicode文字（漢字、ひらがな、全角カタカナなど）: 2バイト
    return 2


def extract_substring_by_width(text, start_pos, length):
    """文字幅を考慮した部分文字列の抽出"""
    current_pos = 0
    start_char_index = 0
    end_char_index = 0

    # 開始位置を見つける
    for i, char in enumerate(text):
        if current_pos >= start_pos:
            start_char_index = i
            break
        current_pos += get_char_width(char)

    # 終了位置を見つける
    for i, char in enumerate(text[start_char_index:], start_char_index):
        if current_pos >= start_pos + length:
            end_char_index = i
            break
        current_pos += get_char_width(char)
    else:
        end_char_index = len(text)

    return text[start_char_index:end_char_index].strip()


def extract_fixed_position_data(line):
    """固定位置からデータを抽出（SHIFT-JIS文字幅ベース）"""
    if len(line) < 200:  # 最小限の長さチェック
        return None

    try:
        # 基本情報（文字幅位置ベース）
        touban = extract_substring_by_width(line, 0, 4)
        name_kanji = extract_substring_by_width(line, 4, 16)
        name_kana = extract_substring_by_width(line, 20, 15)
        shibu = extract_substring_by_width(line, 35, 4)
        kyu = extract_substring_by_width(line, 39, 2)
        nengou = extract_substring_by_width(line, 41, 1)
        birthday = extract_substring_by_width(line, 42, 6)
        gender = extract_substring_by_width(line, 48, 1)
        age = extract_substring_by_width(line, 49, 2)
        height = extract_substring_by_width(line, 51, 3)
        weight = extract_substring_by_width(line, 54, 2)
        blood_type = extract_substring_by_width(line, 56, 2)

        # 成績データ
        shoritsu = extract_substring_by_width(line, 58, 4)
        fukusho_ritsu = extract_substring_by_width(line, 62, 4)
        ichaku_kaisuu = extract_substring_by_width(line, 66, 3)
        nichaku_kaisuu = extract_substring_by_width(line, 69, 3)
        shussou_kaisuu = extract_substring_by_width(line, 72, 3)
        yuushutsu_kaisuu = extract_substring_by_width(line, 75, 2)
        yuushou_kaisuu = extract_substring_by_width(line, 77, 2)
        heikin_start_timing = extract_substring_by_width(line, 79, 3)

        # コース別統計
        # 1コース
        course1_shinnyuu = extract_substring_by_width(line, 82, 3)
        course1_fukusho = extract_substring_by_width(line, 85, 4)
        course1_heikin_start = extract_substring_by_width(line, 89, 3)
        course1_heikin_junii = extract_substring_by_width(line, 92, 3)

        # 2コース
        course2_shinnyuu = extract_substring_by_width(line, 95, 3)
        course2_fukusho = extract_substring_by_width(line, 98, 4)
        course2_heikin_start = extract_substring_by_width(line, 102, 3)
        course2_heikin_junii = extract_substring_by_width(line, 105, 3)

        # 3コース
        course3_shinnyuu = extract_substring_by_width(line, 108, 3)
        course3_fukusho = extract_substring_by_width(line, 111, 4)
        course3_heikin_start = extract_substring_by_width(line, 115, 3)
        course3_heikin_junii = extract_substring_by_width(line, 118, 3)

        # 4コース
        course4_shinnyuu = extract_substring_by_width(line, 121, 3)
        course4_fukusho = extract_substring_by_width(line, 124, 4)
        course4_heikin_start = extract_substring_by_width(line, 128, 3)
        course4_heikin_junii = extract_substring_by_width(line, 131, 3)

        # 5コース
        course5_shinnyuu = extract_substring_by_width(line, 134, 3)
        course5_fukusho = extract_substring_by_width(line, 137, 4)
        course5_heikin_start = extract_substring_by_width(line, 141, 3)
        course5_heikin_junii = extract_substring_by_width(line, 144, 3)

        # 6コース
        course6_shinnyuu = extract_substring_by_width(line, 147, 3)
        course6_fukusho = extract_substring_by_width(line, 150, 4)
        course6_heikin_start = extract_substring_by_width(line, 154, 3)
        course6_heikin_junii = extract_substring_by_width(line, 157, 3)

        # 級・期間情報
        zenki_kyu = extract_substring_by_width(line, 160, 2)
        zenzenki_kyu = extract_substring_by_width(line, 162, 2)
        zenzenzeki_kyu = extract_substring_by_width(line, 164, 2)
        zenki_nouryoku = extract_substring_by_width(line, 166, 4)
        konki_nouryoku = extract_substring_by_width(line, 170, 4)
        nen = extract_substring_by_width(line, 174, 4)
        ki = extract_substring_by_width(line, 178, 1)
        sanshutu_kikan_ji = extract_substring_by_width(line, 179, 8)
        sanshutu_kikan_shi = extract_substring_by_width(line, 187, 8)
        yousei_ki = extract_substring_by_width(line, 195, 3)

        # 詳細成績データ（1コース）
        course1_1chaku = extract_substring_by_width(line, 198, 3)
        course1_2chaku = extract_substring_by_width(line, 201, 3)
        course1_3chaku = extract_substring_by_width(line, 204, 3)
        course1_4chaku = extract_substring_by_width(line, 207, 3)
        course1_5chaku = extract_substring_by_width(line, 210, 3)
        course1_6chaku = extract_substring_by_width(line, 213, 3)
        course1_f = extract_substring_by_width(line, 216, 2)
        course1_l0 = extract_substring_by_width(line, 218, 2)
        course1_l1 = extract_substring_by_width(line, 220, 2)
        course1_k0 = extract_substring_by_width(line, 222, 2)
        course1_k1 = extract_substring_by_width(line, 224, 2)
        course1_s0 = extract_substring_by_width(line, 226, 2)
        course1_s1 = extract_substring_by_width(line, 228, 2)
        course1_s2 = extract_substring_by_width(line, 230, 2)

        # 詳細成績データ（2コース）
        course2_1chaku = extract_substring_by_width(line, 232, 3)
        course2_2chaku = extract_substring_by_width(line, 235, 3)
        course2_3chaku = extract_substring_by_width(line, 238, 3)
        course2_4chaku = extract_substring_by_width(line, 241, 3)
        course2_5chaku = extract_substring_by_width(line, 244, 3)
        course2_6chaku = extract_substring_by_width(line, 247, 3)
        course2_f = extract_substring_by_width(line, 250, 2)
        course2_l0 = extract_substring_by_width(line, 252, 2)
        course2_l1 = extract_substring_by_width(line, 254, 2)
        course2_k0 = extract_substring_by_width(line, 256, 2)
        course2_k1 = extract_substring_by_width(line, 258, 2)
        course2_s0 = extract_substring_by_width(line, 260, 2)
        course2_s1 = extract_substring_by_width(line, 262, 2)
        course2_s2 = extract_substring_by_width(line, 264, 2)

        # 詳細成績データ（3コース）
        course3_1chaku = extract_substring_by_width(line, 266, 3)
        course3_2chaku = extract_substring_by_width(line, 269, 3)
        course3_3chaku = extract_substring_by_width(line, 272, 3)
        course3_4chaku = extract_substring_by_width(line, 275, 3)
        course3_5chaku = extract_substring_by_width(line, 278, 3)
        course3_6chaku = extract_substring_by_width(line, 281, 3)
        course3_f = extract_substring_by_width(line, 284, 2)
        course3_l0 = extract_substring_by_width(line, 286, 2)
        course3_l1 = extract_substring_by_width(line, 288, 2)
        course3_k0 = extract_substring_by_width(line, 290, 2)
        course3_k1 = extract_substring_by_width(line, 292, 2)
        course3_s0 = extract_substring_by_width(line, 294, 2)
        course3_s1 = extract_substring_by_width(line, 296, 2)
        course3_s2 = extract_substring_by_width(line, 298, 2)

        # 詳細成績データ（4コース）
        course4_1chaku = extract_substring_by_width(line, 300, 3)
        course4_2chaku = extract_substring_by_width(line, 303, 3)
        course4_3chaku = extract_substring_by_width(line, 306, 3)
        course4_4chaku = extract_substring_by_width(line, 309, 3)
        course4_5chaku = extract_substring_by_width(line, 312, 3)
        course4_6chaku = extract_substring_by_width(line, 315, 3)
        course4_f = extract_substring_by_width(line, 318, 2)
        course4_l0 = extract_substring_by_width(line, 320, 2)
        course4_l1 = extract_substring_by_width(line, 322, 2)
        course4_k0 = extract_substring_by_width(line, 324, 2)
        course4_k1 = extract_substring_by_width(line, 326, 2)
        course4_s0 = extract_substring_by_width(line, 328, 2)
        course4_s1 = extract_substring_by_width(line, 330, 2)
        course4_s2 = extract_substring_by_width(line, 332, 2)

        # 詳細成績データ（5コース）
        course5_1chaku = extract_substring_by_width(line, 334, 3)
        course5_2chaku = extract_substring_by_width(line, 337, 3)
        course5_3chaku = extract_substring_by_width(line, 340, 3)
        course5_4chaku = extract_substring_by_width(line, 343, 3)
        course5_5chaku = extract_substring_by_width(line, 346, 3)
        course5_6chaku = extract_substring_by_width(line, 349, 3)
        course5_f = extract_substring_by_width(line, 352, 2)
        course5_l0 = extract_substring_by_width(line, 354, 2)
        course5_l1 = extract_substring_by_width(line, 356, 2)
        course5_k0 = extract_substring_by_width(line, 358, 2)
        course5_k1 = extract_substring_by_width(line, 360, 2)
        course5_s0 = extract_substring_by_width(line, 362, 2)
        course5_s1 = extract_substring_by_width(line, 364, 2)
        course5_s2 = extract_substring_by_width(line, 366, 2)

        # 詳細成績データ（6コース）
        course6_1chaku = extract_substring_by_width(line, 368, 3)
        course6_2chaku = extract_substring_by_width(line, 371, 3)
        course6_3chaku = extract_substring_by_width(line, 374, 3)
        course6_4chaku = extract_substring_by_width(line, 377, 3)
        course6_5chaku = extract_substring_by_width(line, 380, 3)
        course6_6chaku = extract_substring_by_width(line, 383, 3)
        course6_f = extract_substring_by_width(line, 386, 2)
        course6_l0 = extract_substring_by_width(line, 388, 2)
        course6_l1 = extract_substring_by_width(line, 390, 2)
        course6_k0 = extract_substring_by_width(line, 392, 2)
        course6_k1 = extract_substring_by_width(line, 394, 2)
        course6_s0 = extract_substring_by_width(line, 396, 2)
        course6_s1 = extract_substring_by_width(line, 398, 2)
        course6_s2 = extract_substring_by_width(line, 400, 2)

        # コースなし・出身地（最終部分）
        course_nashi_l0 = extract_substring_by_width(line, 402, 2)
        course_nashi_l1 = extract_substring_by_width(line, 404, 2)
        course_nashi_k0 = extract_substring_by_width(line, 406, 2)
        course_nashi_k1 = extract_substring_by_width(line, 408, 2)

        # 出身地（最後の部分）
        # 出身地は全角文字（2バイト）なので文字幅ベースで抽出
        # コースなしK1回数の後（410文字幅位置）から出身地を抽出
        shusshinchi = extract_substring_by_width(line, 410, 6)

    except (IndexError, ValueError) as e:
        print(f"抽出エラー: {e}")
        return None

    return [
        # 基本情報
        format_number(touban),
        convert_fullwidth_spaces_in_name(name_kanji),
        convert_halfwidth_kana_to_fullwidth(name_kana),
        shibu,
        kyu,
        nengou,
        birthday,
        gender,
        format_number(age),
        format_number(height),
        format_number(weight),
        blood_type,
        # 成績データ
        format_decimal(shoritsu, 2),  # 小数点以下2桁
        format_decimal(fukusho_ritsu, 1),  # 小数点以下1桁
        format_number(ichaku_kaisuu),
        format_number(nichaku_kaisuu),
        format_number(shussou_kaisuu),
        format_number(yuushutsu_kaisuu),
        format_number(yuushou_kaisuu),
        format_decimal(heikin_start_timing, 2),  # 小数点以下2桁
        # コース別統計
        format_number(course1_shinnyuu),
        format_decimal(course1_fukusho, 1),
        format_decimal(course1_heikin_start, 2),
        format_decimal(course1_heikin_junii, 2),
        format_number(course2_shinnyuu),
        format_decimal(course2_fukusho, 1),
        format_decimal(course2_heikin_start, 2),
        format_decimal(course2_heikin_junii, 2),
        format_number(course3_shinnyuu),
        format_decimal(course3_fukusho, 1),
        format_decimal(course3_heikin_start, 2),
        format_decimal(course3_heikin_junii, 2),
        format_number(course4_shinnyuu),
        format_decimal(course4_fukusho, 1),
        format_decimal(course4_heikin_start, 2),
        format_decimal(course4_heikin_junii, 2),
        format_number(course5_shinnyuu),
        format_decimal(course5_fukusho, 1),
        format_decimal(course5_heikin_start, 2),
        format_decimal(course5_heikin_junii, 2),
        format_number(course6_shinnyuu),
        format_decimal(course6_fukusho, 1),
        format_decimal(course6_heikin_start, 2),
        format_decimal(course6_heikin_junii, 2),
        # 級・期間情報
        zenki_kyu,
        zenzenki_kyu,
        zenzenzeki_kyu,
        format_decimal(zenki_nouryoku, 2),
        format_decimal(konki_nouryoku, 2),
        format_number(nen),
        format_number(ki),
        format_date_yyyymmdd(sanshutu_kikan_ji),
        format_date_yyyymmdd(sanshutu_kikan_shi),
        format_number(yousei_ki),
        # 詳細成績データ（1コース）
        format_number(course1_1chaku),
        format_number(course1_2chaku),
        format_number(course1_3chaku),
        format_number(course1_4chaku),
        format_number(course1_5chaku),
        format_number(course1_6chaku),
        format_number(course1_f),
        format_number(course1_l0),
        format_number(course1_l1),
        format_number(course1_k0),
        format_number(course1_k1),
        format_number(course1_s0),
        format_number(course1_s1),
        format_number(course1_s2),
        # 詳細成績データ（2コース）
        format_number(course2_1chaku),
        format_number(course2_2chaku),
        format_number(course2_3chaku),
        format_number(course2_4chaku),
        format_number(course2_5chaku),
        format_number(course2_6chaku),
        format_number(course2_f),
        format_number(course2_l0),
        format_number(course2_l1),
        format_number(course2_k0),
        format_number(course2_k1),
        format_number(course2_s0),
        format_number(course2_s1),
        format_number(course2_s2),
        # 詳細成績データ（3コース）
        format_number(course3_1chaku),
        format_number(course3_2chaku),
        format_number(course3_3chaku),
        format_number(course3_4chaku),
        format_number(course3_5chaku),
        format_number(course3_6chaku),
        format_number(course3_f),
        format_number(course3_l0),
        format_number(course3_l1),
        format_number(course3_k0),
        format_number(course3_k1),
        format_number(course3_s0),
        format_number(course3_s1),
        format_number(course3_s2),
        # 詳細成績データ（4コース）
        format_number(course4_1chaku),
        format_number(course4_2chaku),
        format_number(course4_3chaku),
        format_number(course4_4chaku),
        format_number(course4_5chaku),
        format_number(course4_6chaku),
        format_number(course4_f),
        format_number(course4_l0),
        format_number(course4_l1),
        format_number(course4_k0),
        format_number(course4_k1),
        format_number(course4_s0),
        format_number(course4_s1),
        format_number(course4_s2),
        # 詳細成績データ（5コース）
        format_number(course5_1chaku),
        format_number(course5_2chaku),
        format_number(course5_3chaku),
        format_number(course5_4chaku),
        format_number(course5_5chaku),
        format_number(course5_6chaku),
        format_number(course5_f),
        format_number(course5_l0),
        format_number(course5_l1),
        format_number(course5_k0),
        format_number(course5_k1),
        format_number(course5_s0),
        format_number(course5_s1),
        format_number(course5_s2),
        # 詳細成績データ（6コース）
        format_number(course6_1chaku),
        format_number(course6_2chaku),
        format_number(course6_3chaku),
        format_number(course6_4chaku),
        format_number(course6_5chaku),
        format_number(course6_6chaku),
        format_number(course6_f),
        format_number(course6_l0),
        format_number(course6_l1),
        format_number(course6_k0),
        format_number(course6_k1),
        format_number(course6_s0),
        format_number(course6_s1),
        format_number(course6_s2),
        # その他
        format_number(course_nashi_l0),
        format_number(course_nashi_l1),
        format_number(course_nashi_k0),
        format_number(course_nashi_k1),
        remove_fullwidth_spaces(shusshinchi),
    ]


def format_number(value):
    """数値フォーマット（先頭0除去）"""
    if not value or value == "":
        return ""
    try:
        return str(int(value))
    except ValueError:
        return value


def format_decimal(value, decimal_places):
    """小数点フォーマット"""
    if not value or value == "":
        return ""
    try:
        num = int(value)
        divisor = 10**decimal_places
        return str(num / divisor)
    except ValueError:
        return value


def convert_gender(gender):
    """性別変換"""
    if gender == "1":
        return "男"
    elif gender == "2":
        return "女"
    return gender


def convert_nengou(nengou):
    """年号変換"""
    if nengou == "S":
        return "昭和"
    elif nengou == "H":
        return "平成"
    elif nengou == "R":
        return "令和"
    return nengou


def convert_period(period):
    """期変換（e=1前期, l=2後期）"""
    if period == "e":
        return 1
    elif period == "l":
        return 2
    return period


def format_date(date_str, nengou):
    """生年月日フォーマット（年号付き）"""
    if not date_str or len(date_str) != 6:
        return date_str

    try:
        year = date_str[:2]
        month = date_str[2:4]
        day = date_str[4:6]
        nengou_name = convert_nengou(nengou)
        return f"{nengou_name}{int(year)}年{int(month)}月{int(day)}日"
    except ValueError:
        return date_str


def format_date_yyyymmdd(date_str):
    """YYYYMMDD形式の日付フォーマット"""
    if not date_str or len(date_str) != 8:
        return date_str

    try:
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:8]
        return f"{year}-{month}-{day}"
    except ValueError:
        return date_str


def parse_racer_data(file_path):
    """レーサー期別成績ファイルを解析してCSVデータを作成"""
    results = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip("\n\r")
                if line.strip():  # 空行でない場合
                    racer_data = extract_fixed_position_data(line)
                    if racer_data:
                        results.append(racer_data)
                    else:
                        print(f"警告: {line_num}行目のデータを解析できませんでした")
    except UnicodeDecodeError:
        print("エラー: ファイルのエンコーディングがUTF-8ではありません")
        return []
    except Exception as e:
        print(f"エラー: ファイル読み込み中にエラーが発生しました: {e}")
        return []

    # 年(49列目), 期(50列目)を先頭に移動
    for i in range(len(results)):
        row = results[i]
        if len(row) > 50:
            year = row[49]
            period = row[50]
            # 49,50列目を削除して先頭に挿入
            new_row = [year, period] + row[:49] + row[51:]
            results[i] = new_row
    return results


def write_csv(results, output_file, year, period):
    """結果をCSVファイルに出力"""
    headers = [
        "年",
        "期",
        "登番",
        "名前漢字",
        "名前カナ",
        "支部",
        "級",
        "年号",
        "生年月日",
        "性別",
        "年齢",
        "身長",
        "体重",
        "血液型",
        "勝率",
        "複勝率",
        "1着回数",
        "2着回数",
        "出走回数",
        "優出回数",
        "優勝回数",
        "平均スタートタイミング",
        "1コース進入回数",
        "1コース複勝率",
        "1コース平均スタートタイミング",
        "1コース平均スタート順位",
        "2コース進入回数",
        "2コース複勝率",
        "2コース平均スタートタイミング",
        "2コース平均スタート順位",
        "3コース進入回数",
        "3コース複勝率",
        "3コース平均スタートタイミング",
        "3コース平均スタート順位",
        "4コース進入回数",
        "4コース複勝率",
        "4コース平均スタートタイミング",
        "4コース平均スタート順位",
        "5コース進入回数",
        "5コース複勝率",
        "5コース平均スタートタイミング",
        "5コース平均スタート順位",
        "6コース進入回数",
        "6コース複勝率",
        "6コース平均スタートタイミング",
        "6コース平均スタート順位",
        "前期級",
        "前々期級",
        "前々々期級",
        "前期能力指数",
        "今期能力指数",
        "算出期間自",
        "算出期間至",
        "養成期",
        "1コース1着回数",
        "1コース2着回数",
        "1コース3着回数",
        "1コース4着回数",
        "1コース5着回数",
        "1コース6着回数",
        "1コースF回数",
        "1コースL0回数",
        "1コースL1回数",
        "1コースK0回数",
        "1コースK1回数",
        "1コースS0回数",
        "1コースS1回数",
        "1コースS2回数",
        "2コース1着回数",
        "2コース2着回数",
        "2コース3着回数",
        "2コース4着回数",
        "2コース5着回数",
        "2コース6着回数",
        "2コースF回数",
        "2コースL0回数",
        "2コースL1回数",
        "2コースK0回数",
        "2コースK1回数",
        "2コースS0回数",
        "2コースS1回数",
        "2コースS2回数",
        "3コース1着回数",
        "3コース2着回数",
        "3コース3着回数",
        "3コース4着回数",
        "3コース5着回数",
        "3コース6着回数",
        "3コースF回数",
        "3コースL0回数",
        "3コースL1回数",
        "3コースK0回数",
        "3コースK1回数",
        "3コースS0回数",
        "3コースS1回数",
        "3コースS2回数",
        "4コース1着回数",
        "4コース2着回数",
        "4コース3着回数",
        "4コース4着回数",
        "4コース5着回数",
        "4コース6着回数",
        "4コースF回数",
        "4コースL0回数",
        "4コースL1回数",
        "4コースK0回数",
        "4コースK1回数",
        "4コースS0回数",
        "4コースS1回数",
        "4コースS2回数",
        "5コース1着回数",
        "5コース2着回数",
        "5コース3着回数",
        "5コース4着回数",
        "5コース5着回数",
        "5コース6着回数",
        "5コースF回数",
        "5コースL0回数",
        "5コースL1回数",
        "5コースK0回数",
        "5コースK1回数",
        "5コースS0回数",
        "5コースS1回数",
        "5コースS2回数",
        "6コース1着回数",
        "6コース2着回数",
        "6コース3着回数",
        "6コース4着回数",
        "6コース5着回数",
        "6コース6着回数",
        "6コースF回数",
        "6コースL0回数",
        "6コースL1回数",
        "6コースK0回数",
        "6コースK1回数",
        "6コースS0回数",
        "6コースS1回数",
        "6コースS2回数",
        "コースなしL0回数",
        "コースなしL1回数",
        "コースなしK0回数",
        "コースなしK1回数",
        "出身地",
    ]

    # ファイルが存在するかチェック
    file_exists = os.path.exists(output_file)

    # 既存データを読み込んで重複チェック用のセットを作成
    existing_keys = set()
    if file_exists:
        try:
            with open(output_file, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # ヘッダーをスキップ
                for row in reader:
                    if len(row) > 51:  # 年、期、登番が存在する場合
                        key = (
                            row[0],
                            row[1],
                            row[2],
                        )  # 年、期、登番をキーとする（先頭に移動済み）
                        existing_keys.add(key)
        except Exception as e:
            print(f"警告: 既存ファイルの読み込み中にエラーが発生しました: {e}")

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # ヘッダーを書き込み（ファイルが存在しない場合のみ）
        if not file_exists:
            writer.writerow(headers)

        # データを書き込み（重複チェック付き）
        period_num = convert_period(period)
        new_rows_count = 0
        duplicate_count = 0

        for row in results:
            # 年・期・登番（先頭3列）で重複チェック
            key = (
                str(row[0]),  # 年
                str(row[1]),  # 期
                str(row[2]),  # 登番
            )
            if key not in existing_keys:
                writer.writerow(row)
                existing_keys.add(key)
                new_rows_count += 1
            else:
                duplicate_count += 1

        if duplicate_count > 0:
            print(f"重複データ {duplicate_count}件をスキップしました")
        print(f"新規データ {new_rows_count}件を追加しました")


def sort_csv_file(file_path):
    """CSVファイルを年、期、登番でソートする"""
    try:
        # CSVファイルを読み込み
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if len(rows) <= 1:  # ヘッダーのみまたは空の場合
            return

        # ヘッダーと データを分離
        header = rows[0]
        data_rows = rows[1:]

        # データをソート（年、期、登番の順）
        # 年は数値、期は0/1、登番は数値でソート
        def sort_key(row):
            try:
                year = int(row[0])  # 年（先頭）
                period = int(row[1])  # 期（先頭）
                touban = int(row[2])  # 登番（先頭）
                return (year, period, touban)
            except (ValueError, IndexError):
                # エラーの場合は末尾に配置
                return (9999, 9999, 9999)

        sorted_data = sorted(data_rows, key=sort_key)

        # ソート済みデータを書き戻し
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)  # ヘッダーを書き込み
            writer.writerows(sorted_data)  # ソート済みデータを書き込み

    except Exception as e:
        print(f"警告: ソート処理中にエラーが発生しました: {e}")


def convert_fullwidth_spaces_in_name(text):
    """名前漢字の全角スペース変換（1文字削除、2文字以上は半角スペースに変換）"""
    if not text:
        return ""

    import re

    # 2文字以上の連続する全角スペースを半角スペースに変換
    text = re.sub("　{2,}", " ", text)

    # 1文字の全角スペースを削除
    text = text.replace("　", "")

    return text


def remove_fullwidth_spaces(text):
    """全角スペースを削除"""
    if not text:
        return ""
    return text.replace("　", "")


def convert_halfwidth_kana_to_fullwidth(text):
    """半角カタカナを全角カタカナに変換（unicodedataライブラリを使用）"""
    if not text:
        return ""

    # unicodedataのNFKCノーマライゼーションを使用して半角カタカナを全角カタカナに変換
    return unicodedata.normalize("NFKC", text)


def main():
    """メイン関数"""
    if len(sys.argv) != 3:
        print("使用方法: python convert_racer.py <期> <年>")
        print("例: python convert_racer.py e 2025")
        print("  e: 前期, l: 後期")
        sys.exit(1)

    period = sys.argv[1]
    year = sys.argv[2]

    # 期の妥当性チェック
    if period not in ["e", "l"]:
        print("エラー: 期は 'e'（前期）または 'l'（後期）を指定してください")
        sys.exit(1)

    # 年の妥当性チェック
    try:
        year_int = int(year)
        if year_int < 1900 or year_int > 2100:
            raise ValueError
    except ValueError:
        print("エラー: 年は4桁の数値で入力してください")
        sys.exit(1)

    # 入力ファイル名を生成
    input_filename = f"racer_{year}{period}.txt"
    input_path = os.path.join("data", "raw", "racer", input_filename)

    # ファイルの存在確認
    if not os.path.exists(input_path):
        print(f"エラー: ファイル {input_path} が見つかりません")
        sys.exit(1)

    print(f"処理開始: {input_path}")

    # データを解析
    results = parse_racer_data(input_path)

    if not results:
        print("エラー: データが見つかりませんでした")
        sys.exit(1)

    # 出力ファイル名を生成（統一ファイル）
    output_path = os.path.join("data", "racers.csv")

    # 出力ディレクトリの作成
    os.makedirs("data", exist_ok=True)

    # CSVファイルに出力
    write_csv(results, output_path, year, period)

    # データを年、期、登番でソートする
    sort_csv_file(output_path)

    print(f"変換完了: 処理対象 {len(results)}件のデータを {output_path} に処理しました")


if __name__ == "__main__":
    main()
