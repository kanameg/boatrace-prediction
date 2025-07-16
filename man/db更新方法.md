今後programs.csvにデータが追加された場合のデータベース更新方法について、いくつかのアプローチがあります：

## 1. **完全リフレッシュ方式（現在の方法）**

現在のスクリプトは毎回テーブルを再作成します：

```bash
# 既存データを削除して全データを再インポート
./import_programs.sh
```

**メリット**: シンプル、データ整合性が保証される
**デメリット**: データ量が多くなると時間がかかる

## 2. **増分インポート方式**

新しいデータのみを追加するスクリプトを作成しましょう： 

Made changes.

実行権限を付与します： ## 3. **推奨する運用方法**

### **日常の更新**（新しいデータが少ない場合）
```bash
# 増分インポート（重複を自動回避）
cd db
./import_programs_incremental.sh
```

### **定期的なフルリフレッシュ**（月次など）
```bash
# 完全リフレッシュ（データ整合性確保）
cd db
./import_programs.sh
```

### **データ検証**
```bash
# レコード数確認
sqlite3 db/boat_race.db "SELECT COUNT(*) FROM programs;"

# 最新データ確認
sqlite3 db/boat_race.db "SELECT MAX(year), MAX(month), MAX(day) FROM programs;"

# 重複チェック
sqlite3 db/boat_race.db "SELECT year, month, day, venue_code, race_number, COUNT(*) as cnt FROM programs GROUP BY year, month, day, venue_code, race_number HAVING cnt > 1;"
```

## 4. **利点**

- **INSERT OR IGNORE**: UNIQUE制約により重複データを自動回避
- **高速**: 新しいデータのみ処理
- **安全**: 既存データを保護
- **柔軟**: 必要に応じて完全リフレッシュも可能

この方法で、効率的にデータベースを更新できます！