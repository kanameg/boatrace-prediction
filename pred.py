import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# データの準備
data = pd.DataFrame(
    {
        "日付": [
            "2024-11-01",
            "2024-11-01",
            "2024-11-01",
            "2024-11-02",
            "2024-11-02",
            "2024-11-02",
            "2024-11-03",
            "2024-11-03",
            "2024-11-03",
        ],
        "レース名": [
            "スターカップ",
            "スターカップ",
            "スターカップ",
            "ドリーム杯",
            "ドリーム杯",
            "ドリーム杯",
            "チャンピオン杯",
            "チャンピオン杯",
            "チャンピオン杯",
        ],
        "選手名": [
            "田中一郎",
            "山田次郎",
            "佐藤三郎",
            "中村四郎",
            "伊藤五郎",
            "渡辺六郎",
            "鈴木七郎",
            "木村八郎",
            "斎藤九郎",
        ],
        "枠番": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "スタートタイミング": [0.12, 0.08, 0.10, 0.15, 0.12, 0.13, 0.09, 0.11, 0.08],
        "モーター性能": [80, 78, 85, 75, 77, 82, 84, 79, 81],
    }
)

# モデル構築
X = data[["枠番", "スタートタイミング", "モーター性能"]]
y = [1, 0, 1, 1, 0, 0, 1, 0, 1]  # 勝敗ラベル

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

X["勝敗"] = y
print("データ:\n", X)

model = RandomForestClassifier()
model.fit(X_train, y_train)

# 予測の実行
print("テストデータ:", X_test)
predictions = model.predict(X_test)
print("予測結果:", predictions)
