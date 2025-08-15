# Flet Othello Game

Fletフレームワークを使用したオセロゲームです。Webブラウザとデスクトップアプリケーションの両方で動作します。

## 機能

- 🎮 2人対戦モード
- 🤖 AI対戦モード（難易度選択可能）
- 🎨 ダーク/ライトテーマ切り替え
- ↩️ アンドゥ機能
- 📊 リアルタイムスコア表示
- 📝 手番履歴表示

## セットアップ

### 前提条件

- Python 3.11以上
- uv (Pythonパッケージマネージャー)

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/ayutaz/flet-othello.git
cd flet-othello

# uvで依存関係をインストール
uv pip install -r requirements.txt

# または開発環境用
uv pip install -e ".[dev]"
```

## 実行方法

### 開発環境で実行

```bash
# アプリを起動
flet run src/main.py

# ホットリロード付きでWeb版を起動
flet run src/main.py --web --port 8000
```

### ビルド

#### Web版

```bash
flet build web --project "Othello Game" --description "Flet Othello Game"
```

ビルド成果物は`build/web`ディレクトリに生成されます。

#### デスクトップ版

```bash
# Windows
flet build windows

# macOS
flet build macos

# Linux
flet build linux
```

## デプロイ

### GitHub Pages

mainブランチにpushすると、GitHub Actionsが自動的にビルドしてGitHub Pagesにデプロイします。

デプロイ先URL: `https://ayutaz.github.io/flet-othello/`

### ローカルサーバー

```bash
# ビルド
flet build web

# Pythonの簡易サーバーで起動
cd build/web
python -m http.server 8000
```

## 開発

### テスト実行

```bash
pytest
```

### コードフォーマット

```bash
black src/
```

### リンター

```bash
ruff check src/
```

## プロジェクト構造

```
flet-othello/
├── src/
│   ├── main.py          # エントリーポイント
│   ├── game/            # ゲームロジック
│   │   ├── board.py     # ボード管理
│   │   ├── game.py      # ゲーム進行管理
│   │   └── ai.py        # AI実装
│   └── ui/              # UI関連
│       ├── board_ui.py  # ボードUI
│       ├── controls.py  # コントロールUI
│       └── theme.py     # テーマ設定
├── tests/               # テストコード
├── docs/                # ドキュメント
│   └── specification.md # 仕様書
├── build/               # ビルド成果物
├── requirements.txt     # 依存関係
└── pyproject.toml      # プロジェクト設定
```

## ライセンス

MIT License

## 作者

[ayutaz](https://github.com/ayutaz)