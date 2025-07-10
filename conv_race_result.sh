# レース結果データを変換
#!/bin/bash

# ----------------------------------
# 引数チェック
# ----------------------------------
if [ $# -ne 3 ]; then
  echo "Usage: $0 <year> <month> <day>"
  exit 1
fi
YEAR=$1 
MONTH=$2
DAY=$3

# ----------------------------------
# 年月日のフォーマットチェック
# ----------------------------------
if [[ $YEAR =~ ^20[0-9]{2}$ ]]; then
    # YEARが20XX形式の場合は20を削除
    YEAR=$(echo $YEAR | sed 's/^20//')
elif [[ $YEAR =~ ^[0-9]{2}$ ]]; then
    # YEARがYY形式の場合はそのまま使用
    :
else
    echo "Invalid year format. Use 20XX or YY."
    exit 1
fi

if [ ${#MONTH} -eq 1 ]; then
    # 月が1桁の場合は0を付ける
    MONTH="0${MONTH}"
fi

if [ ${#DAY} -eq 1 ]; then
    # 日が1桁の場合は0を付ける
    DAY="0${DAY}"
fi

# ----------------------------------
# 圧縮ファイルからのデータを展開
# ----------------------------------
ARCHIVE=data/raw/race_result/k${YEAR}${MONTH}${DAY}.lzh
if [ -f ${ARCHIVE} ]; then
    lha x ${ARCHIVE} -o k${YEAR}${MONTH}${DAY}.txt
else
    echo "Archive file ${ARCHIVE} not found."
    exit 1
fi

# ----------------------------------
# データのコード変換
# ----------------------------------
# 変換成功したら、元のファイルを削除
iconv -f sjis -t utf8 k${YEAR}${MONTH}${DAY}.txt > k${YEAR}${MONTH}${DAY}_u8.txt
if [ -f k${YEAR}${MONTH}${DAY}_utf8.txt ]; then
    rm -f k${YEAR}${MONTH}${DAY}.txt
fi
