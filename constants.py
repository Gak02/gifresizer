"""
GIF Resizer アプリケーションの定数定義
"""

# ファイルサイズ制限
MAX_FILE_SIZE_MB = 200
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Slackスタンプ要件
SLACK_STAMP_MAX_SIZE_KB = 128
SLACK_STAMP_MAX_SIZE_BYTES = SLACK_STAMP_MAX_SIZE_KB * 1024
SLACK_STAMP_SIZE = 128
SLACK_STAMP_MAX_FRAMES = 50

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

# Slackスタンプ専用プリセット
SLACK_STAMP_PRESETS = [
    "Slackスタンプ (128×128)",
    "Slackスタンプ 最適化 (128×128, 50フレーム以下)",
    "Slackスタンプ 軽量 (128×128, 128KB以下)"
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

# 最適化設定
SLACK_OPTIMIZATION_QUALITY_START = 30  # より低い品質から開始
SLACK_OPTIMIZATION_QUALITY_MIN = 5     # より低い品質まで下げる
SLACK_OPTIMIZATION_QUALITY_STEP = 5    # より細かいステップ
SLACK_OPTIMIZATION_DURATION_MAX = 50   # より短いフレーム間隔

# 強力最適化設定
SLACK_AGGRESSIVE_MAX_FRAMES = 20       # より少ないフレーム数
SLACK_AGGRESSIVE_DURATION = 30         # より短いフレーム間隔

# pygifsicle最適化設定
PYGIFSICLE_OPTIMIZATION_LEVELS = {
    "standard": 1,      # 標準最適化
    "optimized": 2,     # 高最適化
    "aggressive": 3     # 強力最適化
} 