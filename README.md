# 🎞️ GIF Resizer

Streamlitを使用したGIFファイルリサイズツールです。

## ✨ 機能

- **GIFファイルのアップロードとリサイズ**
- **複数のリサイズ方法**: カスタムサイズ、比率指定、プリセットサイズ
- **アスペクト比の維持オプション**
- **リサイズ前後の比較表示**
- **詳細なファイル情報表示**（フレーム数、ファイルサイズなど）
- **ダウンロード機能**

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. アプリの起動

#### 推奨方法（403エラー回避）
```bash
python run_app.py --disable-xsrf
```

#### 通常の起動
```bash
streamlit run gif_resizer.py
```

#### カスタム設定での起動
```bash
python run_app.py --disable-xsrf --port 9876 --host 0.0.0.0
```

## 📖 使用方法

1. **GIFファイルをアップロード**
   - 対応形式: `.gif`
   - 最大ファイルサイズ: 200MB

2. **リサイズ方法を選択**
   - **カスタムサイズ**: 幅と高さを個別指定
   - **比率指定**: パーセンテージで指定（10%〜200%）
   - **プリセットサイズ**: 64x64, 128x128, 256x256, 480x480, 512x512

3. **オプション設定**
   - アスペクト比の維持（推奨）

4. **リサイズ実行**
   - 処理完了後、ダウンロード可能

## 🔧 トラブルシューティング

### 403エラーが発生する場合

1. **XSRF保護を無効にして起動**
   ```bash
   python run_app.py --disable-xsrf
   ```

2. **ブラウザのキャッシュをクリア**
   - `Ctrl+Shift+R` (Windows/Linux)
   - `Cmd+Shift+R` (Mac)

3. **別のポートで起動**
   ```bash
   python run_app.py --port 9876
   ```

### ファイルアップロードが失敗する場合

- ファイルサイズが200MB以下か確認
- ファイルが正常なGIF形式か確認
- ブラウザを更新して再試行

## 🏗️ アーキテクチャ

### ファイル構成
```
slackstamp_gif_resizer/
├── gif_resizer.py          # メインアプリケーション
├── gif_processor.py        # GIF処理のコア機能
├── ui_components.py        # UIコンポーネント
├── utils.py               # ユーティリティ関数
├── constants.py           # 定数定義
├── run_app.py            # 起動スクリプト
├── requirements.txt       # 依存関係
├── .streamlit/
│   └── config.toml       # Streamlit設定
└── README.md             # ドキュメント
```

### 設計原則
- **単一責任原則**: 各モジュールが明確な責任を持つ
- **DRY原則**: コードの重複を避ける
- **エラーハンドリング**: 包括的なエラー処理
- **パフォーマンス**: 大きなファイルの効率的な処理

## 🌐 デプロイ

### Streamlit Community Cloud

1. GitHubにリポジトリをプッシュ
2. [share.streamlit.io](https://share.streamlit.io) にアクセス
3. GitHubリポジトリを選択
4. デプロイ

### 必要なファイル

- `gif_resizer.py` - メインアプリケーション
- `requirements.txt` - 依存関係
- `.streamlit/config.toml` - Streamlit設定

## 📊 技術仕様

- **フレームワーク**: Streamlit >= 1.28.0
- **画像処理**: Pillow >= 10.0.0
- **対応形式**: GIF
- **最大ファイルサイズ**: 200MB
- **最小画像サイズ**: 10px
- **最大画像サイズ**: 2000px

## 🔄 更新履歴

### v2.0.0 (リファクタリング版)
- モジュール分割による保守性向上
- エラーハンドリングの改善
- パフォーマンス最適化
- コードの可読性向上

## 📄 ライセンス

MIT License 