"""
GIF Resizer アプリケーションの定数定義
"""

# ファイルサイズ制限
MAX_FILE_SIZE_MB = 200
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# 画像サイズ制限
MIN_IMAGE_SIZE = 10
MAX_IMAGE_SIZE = 2000

# スケール制限
MIN_SCALE_PERCENT = 10
MAX_SCALE_PERCENT = 200
DEFAULT_SCALE_PERCENT = 100

# プリセットサイズ
PRESET_SIZES = [
    "64x64",
    "128x128", 
    "256x256",
    "480x480",
    "512x512"
]

# リサイズ方法
RESIZE_METHODS = [
    "カスタムサイズ",
    "比率指定", 
    "プリセットサイズ"
]

# デフォルトフレーム間隔（ミリ秒）
DEFAULT_DURATION = 100

# デフォルトループ回数（0 = 無限ループ）
DEFAULT_LOOP = 0 