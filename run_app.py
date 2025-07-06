#!/usr/bin/env python3
"""
GIF Resizer アプリの起動スクリプト
XSRF保護を無効にして403エラーを回避
"""

import subprocess
import sys
import os
import argparse

def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(description="GIF Resizer アプリの起動スクリプト")
    parser.add_argument(
        "--disable-xsrf", 
        action="store_true", 
        help="XSRF保護を無効にする（403エラー回避）"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8501, 
        help="サーバーポート（デフォルト: 8501）"
    )
    parser.add_argument(
        "--host", 
        default="localhost", 
        help="サーバーホスト（デフォルト: localhost）"
    )
    return parser.parse_args()

def main():
    """アプリを起動する"""
    args = parse_arguments()
    
    print("🎞️ GIF Resizer を起動しています...")
    
    if args.disable_xsrf:
        print("XSRF保護を無効にして起動します（403エラー回避）")
    
    # 現在のディレクトリを取得
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Streamlitアプリを起動
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "gif_resizer.py",
        f"--server.port={args.port}",
        f"--server.address={args.host}"
    ]
    
    # XSRF保護を無効にする場合
    if args.disable_xsrf:
        cmd.append("--server.enableXsrfProtection=false")
    
    try:
        print(f"起動コマンド: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=current_dir, check=True)
    except KeyboardInterrupt:
        print("\n👋 アプリを終了しました")
    except subprocess.CalledProcessError as e:
        print(f"❌ アプリの起動に失敗しました: {e}")
        print("対処法:")
        print("1. 依存関係がインストールされているか確認: pip install -r requirements.txt")
        print("2. ポートが使用中でないか確認")
        print("3. --port オプションで別のポートを指定")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlitが見つかりません")
        print("対処法: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main() 