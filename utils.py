"""
GIF Resizer アプリケーションのユーティリティ関数
"""

import io
from PIL import Image
from constants import (
    MAX_FILE_SIZE_BYTES, 
    DEFAULT_DURATION, 
    DEFAULT_LOOP,
    MIN_IMAGE_SIZE,
    MAX_IMAGE_SIZE
)

def validate_file_size(file_bytes):
    """
    ファイルサイズを検証する
    
    Args:
        file_bytes: ファイルのバイトデータ
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        file_size_mb = len(file_bytes) / (1024 * 1024)
        return False, f"ファイルサイズが大きすぎます。最大{MAX_FILE_SIZE_BYTES // (1024 * 1024)}MBまで対応しています。現在のサイズ: {file_size_mb:.1f}MB"
    return True, None

def validate_image_size(width, height):
    """
    画像サイズを検証する
    
    Args:
        width: 幅
        height: 高さ
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
        return False, f"画像サイズが小さすぎます。最小{MIN_IMAGE_SIZE}px必要です。"
    
    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        return False, f"画像サイズが大きすぎます。最大{MAX_IMAGE_SIZE}pxまで対応しています。"
    
    return True, None

def calculate_aspect_ratio(width, height):
    """
    アスペクト比を計算する
    
    Args:
        width: 幅
        height: 高さ
    
    Returns:
        float: アスペクト比
    """
    if height == 0:
        return 1.0  # ゼロ除算を防ぐ
    return width / height

def adjust_size_for_aspect_ratio(target_width, target_height, original_width, original_height):
    """
    アスペクト比を維持してサイズを調整する
    
    Args:
        target_width: 目標幅
        target_height: 目標高さ
        original_width: 元の幅
        original_height: 元の高さ
    
    Returns:
        tuple: (adjusted_width, adjusted_height)
    """
    aspect_ratio = calculate_aspect_ratio(original_width, original_height)
    target_ratio = calculate_aspect_ratio(target_width, target_height)
    
    if target_ratio > aspect_ratio:
        # 幅が広すぎる場合、高さに合わせる
        adjusted_width = int(target_height * aspect_ratio)
        adjusted_height = target_height
    else:
        # 高さが高すぎる場合、幅に合わせる
        adjusted_width = target_width
        adjusted_height = int(target_width / aspect_ratio)
    
    return adjusted_width, adjusted_height

def format_file_size(bytes_size):
    """
    ファイルサイズを読みやすい形式にフォーマットする
    
    Args:
        bytes_size: バイトサイズ
    
    Returns:
        str: フォーマットされたサイズ
    """
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

def calculate_size_change(original_size, new_size):
    """
    サイズ変化を計算する
    
    Args:
        original_size: 元のサイズ
        new_size: 新しいサイズ
    
    Returns:
        float: 変化率（%）
    """
    if original_size == 0:
        return 0.0
    return (new_size - original_size) / original_size * 100

def get_gif_info(gif_bytes):
    """
    GIFファイルの情報を取得する
    
    Args:
        gif_bytes: GIFファイルのバイトデータ
    
    Returns:
        dict: GIF情報
    """
    try:
        gif = Image.open(io.BytesIO(gif_bytes))
        frames = []
        
        # フレーム数をカウント
        frame_count = 0
        while True:
            try:
                gif.seek(frame_count)
                frames.append(gif.copy())
                frame_count += 1
            except EOFError:
                break
        
        return {
            'width': gif.size[0],
            'height': gif.size[1],
            'frame_count': frame_count,
            'duration': gif.info.get('duration', DEFAULT_DURATION),
            'loop': gif.info.get('loop', DEFAULT_LOOP),
            'format': gif.format
        }
    except Exception as e:
        raise ValueError(f"GIFファイルの読み込みに失敗しました: {str(e)}")

def create_download_filename(original_name, new_width, new_height):
    """
    ダウンロード用のファイル名を作成する
    
    Args:
        original_name: 元のファイル名
        new_width: 新しい幅
        new_height: 新しい高さ
    
    Returns:
        str: ダウンロード用ファイル名
    """
    import os
    name_without_ext = os.path.splitext(original_name)[0]
    return f"{name_without_ext}_resized_{new_width}x{new_height}.gif" 