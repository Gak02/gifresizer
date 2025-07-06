"""
GIF処理のコア機能
"""

import io
from PIL import Image
from constants import DEFAULT_DURATION, DEFAULT_LOOP, SLACK_STAMP_MAX_SIZE_BYTES
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
    
    def resize(self, new_width, new_height, optimize_for_slack=False, max_frames=None):
        """
        GIFをリサイズする
        
        Args:
            new_width: 新しい幅
            new_height: 新しい高さ
            optimize_for_slack: Slackスタンプ用に最適化するかどうか
            max_frames: 最大フレーム数（Noneの場合は制限なし）
        
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
                    # フレーム数制限チェック
                    if max_frames and frame_index >= max_frames:
                        break
                    
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
            # Slackスタンプ用の最適化設定
            save_kwargs = {
                'format': 'GIF',
                'save_all': True,
                'append_images': frames[1:],
                'duration': self.original_info['duration'],
                'loop': self.original_info['loop'],
                'optimize': True
            }
            
            if optimize_for_slack:
                # Slackスタンプ用の最適化
                save_kwargs.update({
                    'optimize': True,
                    'quality': 85,  # 品質を少し下げてサイズ削減
                    'transparency': 0,  # 透明度を無効化
                })
            
            # 最初のフレームを保存し、残りのフレームを追加
            frames[0].save(output, **save_kwargs)
            
            # Slackスタンプ用の追加最適化
            if optimize_for_slack:
                result_bytes = output.getvalue()
                # 128KB以下になるまで品質を下げる
                while len(result_bytes) > SLACK_STAMP_MAX_SIZE_BYTES and save_kwargs.get('quality', 85) > 30:
                    output = io.BytesIO()
                    save_kwargs['quality'] = save_kwargs.get('quality', 85) - 5
                    frames[0].save(output, **save_kwargs)
                    result_bytes = output.getvalue()
                
                return result_bytes
            
        except Exception as e:
            raise ValueError(f"GIF保存中にエラーが発生しました: {str(e)}")
        
        return output.getvalue()
    
    def create_slack_stamp(self, optimization_level="standard"):
        """
        Slackスタンプ用のGIFを作成
        
        Args:
            optimization_level: 最適化レベル ("standard", "optimized", "lightweight")
        
        Returns:
            bytes: Slackスタンプ用GIFのバイトデータ
        """
        from constants import SLACK_STAMP_SIZE, SLACK_STAMP_MAX_FRAMES, SLACK_STAMP_MAX_SIZE_BYTES, SLACK_STAMP_MAX_SIZE_KB
        
        if optimization_level == "standard":
            # 標準的なSlackスタンプ
            return self.resize(SLACK_STAMP_SIZE, SLACK_STAMP_SIZE)
        
        elif optimization_level == "optimized":
            # フレーム数制限付き
            return self.resize(SLACK_STAMP_SIZE, SLACK_STAMP_SIZE, 
                             optimize_for_slack=True, max_frames=SLACK_STAMP_MAX_FRAMES)
        
        elif optimization_level == "lightweight":
            # 128KB以下に最適化
            result = self.resize(SLACK_STAMP_SIZE, SLACK_STAMP_SIZE, 
                               optimize_for_slack=True, max_frames=SLACK_STAMP_MAX_FRAMES)
            
            # サイズチェック
            if len(result) > SLACK_STAMP_MAX_SIZE_BYTES:
                raise ValueError(f"Slackスタンプのサイズ制限（{SLACK_STAMP_MAX_SIZE_KB}KB）を超えています。"
                               f"現在のサイズ: {len(result) / 1024:.1f}KB")
            
            return result
        
        else:
            raise ValueError("無効な最適化レベルです")
    
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