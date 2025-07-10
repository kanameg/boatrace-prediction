import re
import csv

def extract_race_info(file_path):
    """
    k250709_u8.txtファイルから詳細なレース情報を抽出してCSVファイルに保存する
    """
    race_data = []
    
    # 競艇場名と番号のマッピング
    venue_mapping = {
        '大村': '24', '唐津': '23', '若松': '20', '宮島': '17', 
        '鳴門': '14', '尼崎': '13', 'びわこ': '11', '三国': '10',
        '常滑': '08', '蒲郡': '07', '多摩川': '05', '江戸川': '02', '桐生': '01'
    }
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    lines = content.split('\n')
    current_venue = None
    current_venue_code = None
    current_date = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 日付の抽出 (例: "第 6日          2025/ 7/ 9")
        date_match = re.search(r'(\d{4})/\s*(\d{1,2})/\s*(\d{1,2})', line)
        if date_match:
            year, month, day = date_match.groups()
            current_date = {'year': year, 'month': month.zfill(2), 'day': day.zfill(2)}
        
        # ボートレース場の検索 (全角スペースで区切られた場名)
        venue_match = re.search(r'ボートレース([^　\s\n]+(?:　[^　\s\n]+)*)', line)
        if venue_match:
            venue_name = venue_match.group(1).replace('　', '')
            current_venue = venue_name
            current_venue_code = venue_mapping.get(venue_name, '00')
            i += 1
            continue
        
        # レース情報の開始を検索 (例: "   1R       一般")
        race_header_match = re.match(r'^\s*(\d+)R\s+.*?H(\d+)m\s+(.*?)\s+風\s+(.*?)\s+(\d+)m\s+波\s+(\d+)cm', line)
        if race_header_match and current_venue and current_date:
            race_number = race_header_match.group(1)
            distance = race_header_match.group(2)
            weather = race_header_match.group(3).strip()
            wind_direction = race_header_match.group(4).strip()
            wind_speed = race_header_match.group(5)
            wave_height = race_header_match.group(6)
            
            # 次の行から着順データを読む
            i += 1
            # ヘッダー行をスキップ
            while i < len(lines) and not lines[i].strip().startswith('01'):
                i += 1
            
            # 着順データを抽出
            position = 1
            while i < len(lines) and position <= 6:
                data_line = lines[i].strip()
                if not data_line or data_line.startswith('単勝') or data_line.startswith('複勝'):
                    break
                
                # 着順データのパターン: "  01  5 3784 中　島　　友　和 40   75  6.89   5    0.10     1.51.0"
                race_data_match = re.match(r'^\s*0?(\d)\s+(\d)\s+(\d+)\s+.*?\s+(\d+)\s+(\d+)\s+([\d.]+)\s+(\d)\s+([\d.-]+)\s+([\d.:]+|\.)\s*', data_line)
                if race_data_match:
                    boat_number = race_data_match.group(2)
                    registration_number = race_data_match.group(3)
                    motor_number = race_data_match.group(4)
                    boat_number_data = race_data_match.group(5)
                    exhibition_time = race_data_match.group(6)
                    approach_number = race_data_match.group(7)
                    start_timing = race_data_match.group(8)
                    race_time = race_data_match.group(9)
                    
                    race_data.append({
                        '年': current_date['year'],
                        '月': current_date['month'],
                        '日': current_date['day'],
                        '競艇場番号': current_venue_code,
                        'レース番号': race_number,
                        '距離': distance,
                        '天候': weather,
                        '風向き': wind_direction,
                        '風速': wind_speed,
                        '波高': wave_height,
                        '着': str(position),
                        '艇': boat_number,
                        '登番': registration_number,
                        'モーター': motor_number,
                        'ボート': boat_number_data,
                        '展示タイム': exhibition_time,
                        '進入番号': approach_number,
                        'スタートタイミング': start_timing,
                        'レースタイム': race_time if race_time != '.' else ''
                    })
                    position += 1
                
                i += 1
            continue
        
        i += 1
    
    return race_data

def save_to_csv(race_data, output_file):
    """
    抽出したデータをCSVファイルに保存
    """
    fieldnames = ['年', '月', '日', '競艇場番号', 'レース番号', '距離', '天候', '風向き', '風速', '波高', 
                  '着', '艇', '登番', 'モーター', 'ボート', '展示タイム', '進入番号', 'スタートタイミング', 'レースタイム']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in race_data:
            writer.writerow(row)

def main():
    input_file = 'k250709_u8.txt'
    output_file = 'race_info.csv'
    
    try:
        # レース情報を抽出
        race_data = extract_race_info(input_file)
        
        # CSVファイルに保存
        save_to_csv(race_data, output_file)
        
        print(f"抽出完了: {len(race_data)}件のレース情報を{output_file}に保存しました。")
        
        # 結果の一部を表示
        print("\n抽出されたデータの例:")
        for i, data in enumerate(race_data[:10]):  # 最初の10件を表示
            print(f"{i+1}. 競艇場: {data['競艇場番号']}, レース番号: {data['レース番号']}, 着順: {data['着']}, 艇番: {data['艇']}")
        
        if len(race_data) > 10:
            print(f"... (他 {len(race_data) - 10} 件)")
            
    except FileNotFoundError:
        print(f"エラー: ファイル '{input_file}' が見つかりません。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
