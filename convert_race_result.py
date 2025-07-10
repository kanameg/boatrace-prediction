import sys

def get_args():
    if len(sys.argv) != 4:
        print("Usage: python convert_race_result.py <year> <month> <day>")
        sys.exit(1)
    year = sys.argv[1]
    month = sys.argv[2]
    day = sys.argv[3]
    return year, month, day

if __name__ == "__main__":
    year, month, day = get_args()
    if len(year) == 4:
        year = year[-2:]
    if len(month) == 1:
        month = "0" + month
    if len(day) == 1:
        day = "0" + day
    print(f"Year: {year}, Month: {month}, Day: {day}")    

    # ファイル名をyear, month, dayのから生成
    filename = f"k{year}{month}{day}_u8.txt"

    # ファイルを1行ずつ読み込み、出力
    try:
        with open(filename, "r") as file:
            for line in file:
                print(line.rstrip())
                # ここで必要な抽出処理を行う
    except FileNotFoundError:
        print(f"File {filename} not found.")
