リモートブランチの状態を確認するためのコマンド
```bash
git fetch --prune
```

すでに削除されたリモートブランチに基づいてローカルブランチを削除する
```bash
git branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git branch -d
```


プルリクエストを作成
```
#69のプルリクエストを作成
```

```bash
```
