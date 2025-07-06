"""
GIF処理のコア機能
"""

import io
from PIL import Image
from constants import DEFAULT_DURATION, DEFAULT_LOOP
from utils import validate_image_size

class GIFProcessor:
    """GIFファイルの処理を行うクラス"""
    
    def __init__(self, gif_bytes):
        """
        GIFProcessorを初期化
        
        Args:
            gif_bytes: GIFファイルのバイトデータ
        """
        self.gif_bytes = gif_bytes
        self.original_gif = Image.open(io.BytesIO(gif_bytes))
        self.original_info = self._extract_gif_info()
    
    def _extract_gif_info(self):
        """
        GIFファイルの情報を抽出
        
        Returns:
            dict: GIF情報
        """
        return {
            'width': self.original_gif.size[0],
            'height': self.original_gif.size[1],
            'duration': self.original_gif.info.get('duration', DEFAULT_DURATION),
            'loop': self.original_gif.info.get('loop', DEFAULT_LOOP),
            'format': self.original_gif.format
        }
    
    def get_frame_count(self):
        """
        フレーム数を取得
        
        Returns:
            int: フレーム数
        """
        frame_count = 0
        gif = Image.open(io.BytesIO(self.gif_bytes))
        
        while True:
            try:
                gif.seek(frame_count)
                frame_count += 1
            except EOFError:
                break
        
        return frame_count
    
    def resize(self, new_width, new_height):
        """
        GIFをリサイズする
        
        Args:
            new_width: 新しい幅
            new_height: 新しい高さ
        
        Returns:
            bytes: リサイズされたGIFのバイトデータ
        
        Raises:
            ValueError: サイズが無効な場合
        """
        # サイズの検証
        is_valid, error_msg = validate_image_size(new_width, new_height)
        if not is_valid:
            raise ValueError(error_msg)
        
        # PILでGIFを開く
        gif = Image.open(io.BytesIO(self.gif_bytes))
        
        # リサイズされたフレームを格納するリスト
        frames = []
        
        try:
            # GIFの各フレームを処理
            frame_index = 0
            while True:
                try:
                    # フレームをリサイズ
                    gif.seek(frame_index)
                    frame = gif.copy()
                    frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    frames.append(frame)
                    frame_index += 1
                except EOFError:
                    # 全フレームを処理完了
                    break
        except Exception as e:
            raise ValueError(f"フレーム処理中にエラーが発生しました: {str(e)}")
        
        if not frames:
            raise ValueError("有効なフレームが見つかりませんでした")
        
        # リサイズされたGIFを保存
        output = io.BytesIO()
        
        try:
            # 最初のフレームを保存し、残りのフレームを追加
            frames[0].save(
                output,
                format='GIF',
                save_all=True,
                append_images=frames[1:],
                duration=self.original_info['duration'],
                loop=self.original_info['loop'],
                optimize=True  # ファイルサイズを最適化
            )
        except Exception as e:
            raise ValueError(f"GIF保存中にエラーが発生しました: {str(e)}")
        
        return output.getvalue()
    
    def get_info(self):
        """
        GIF情報を取得
        
        Returns:
            dict: GIF情報
        """
        return {
            **self.original_info,
            'frame_count': self.get_frame_count(),
            'file_size': len(self.gif_bytes)
        } 