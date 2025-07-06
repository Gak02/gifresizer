"""
GIF処理のコア機能
"""

import io
import tempfile
import os
from PIL import Image
from constants import (
    DEFAULT_DURATION, 
    DEFAULT_LOOP, 
    SLACK_STAMP_MAX_SIZE_BYTES,
    SLACK_OPTIMIZATION_QUALITY_START,
    SLACK_OPTIMIZATION_QUALITY_MIN,
    SLACK_OPTIMIZATION_QUALITY_STEP,
    SLACK_OPTIMIZATION_DURATION_MAX,
    SLACK_AGGRESSIVE_MAX_FRAMES,
    SLACK_AGGRESSIVE_DURATION,
    PYGIFSICLE_OPTIMIZATION_LEVELS
)
from utils import validate_image_size

# pygifsicleのインポート（オプション）
try:
    from pygifsicle import optimize
    PYGIFSICLE_AVAILABLE = True
except ImportError:
    PYGIFSICLE_AVAILABLE = False

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
        
        # Slackスタンプ用の最適化
        if optimize_for_slack and max_frames:
            # フレーム数を制限（最初の50フレームのみ使用）
            frames = frames[:max_frames]
        
        # リサイズされたGIFを保存
        output = io.BytesIO()
        
        try:
            # 基本設定
            save_kwargs = {
                'format': 'GIF',
                'save_all': True,
                'append_images': frames[1:] if len(frames) > 1 else [],
                'duration': self.original_info['duration'],
                'loop': self.original_info['loop'],
                'optimize': True
            }
            
            if optimize_for_slack:
                # Slackスタンプ用の最適化設定
                save_kwargs.update({
                    'optimize': True,
                    'quality': SLACK_OPTIMIZATION_QUALITY_START,  # より低い品質でサイズ削減
                    'transparency': 0,  # 透明度を無効化
                    'disposal': 2,  # フレーム間の処理方法を最適化
                })
                
                # フレーム間隔を短縮してファイルサイズを削減
                save_kwargs['duration'] = min(self.original_info['duration'], SLACK_OPTIMIZATION_DURATION_MAX)
                
                # 色数を削減（256色→128色）
                for i, frame in enumerate(frames):
                    frames[i] = frame.quantize(colors=128, method=2)
            
            # 最初のフレームを保存し、残りのフレームを追加
            frames[0].save(output, **save_kwargs)
            
            # Slackスタンプ用の追加最適化
            if optimize_for_slack:
                result_bytes = output.getvalue()
                quality = save_kwargs.get('quality', SLACK_OPTIMIZATION_QUALITY_START)
                
                # 128KB以下になるまで品質を下げる
                while len(result_bytes) > SLACK_STAMP_MAX_SIZE_BYTES and quality > SLACK_OPTIMIZATION_QUALITY_MIN:
                    output = io.BytesIO()
                    quality -= SLACK_OPTIMIZATION_QUALITY_STEP
                    save_kwargs['quality'] = quality
                    frames[0].save(output, **save_kwargs)
                    result_bytes = output.getvalue()
                
                # pygifsicleで最終最適化
                result_bytes = self.optimize_with_pygifsicle(result_bytes, "optimized")
                
                return result_bytes
            
        except Exception as e:
            raise ValueError(f"GIF保存中にエラーが発生しました: {str(e)}")
        
        result_bytes = output.getvalue()
        
        # 通常のリサイズでも軽度の最適化を適用
        if PYGIFSICLE_AVAILABLE:
            result_bytes = self.optimize_with_pygifsicle(result_bytes, "standard")
        
        return result_bytes
    
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
            # 標準的なSlackスタンプ（128×128pxのみ）
            return self.resize(SLACK_STAMP_SIZE, SLACK_STAMP_SIZE)
        
        elif optimization_level == "optimized":
            # フレーム数制限付き（50フレーム以下）
            result = self.resize(SLACK_STAMP_SIZE, SLACK_STAMP_SIZE, 
                               optimize_for_slack=True, max_frames=SLACK_STAMP_MAX_FRAMES)
            
            # フレーム数チェック
            temp_processor = GIFProcessor(result)
            frame_count = temp_processor.get_frame_count()
            if frame_count > SLACK_STAMP_MAX_FRAMES:
                raise ValueError(f"フレーム数制限（{SLACK_STAMP_MAX_FRAMES}フレーム）を超えています。"
                               f"現在のフレーム数: {frame_count}")
            
            return result
        
        elif optimization_level == "lightweight":
            # 128KB以下に最適化（50フレーム以下 + 128KB以下）
            result = self.resize(SLACK_STAMP_SIZE, SLACK_STAMP_SIZE, 
                               optimize_for_slack=True, max_frames=SLACK_STAMP_MAX_FRAMES)
            
            # pygifsicleで強力な最適化を適用
            result = self.optimize_with_pygifsicle(result, "aggressive")
            
            # サイズチェックと段階的最適化
            optimization_steps = [
                ("標準最適化", lambda: result),
                ("強力最適化", lambda: self._force_optimize_for_slack(result)),
                ("超強力最適化", lambda: self._ultra_optimize_for_slack(result))
            ]
            
            for step_name, optimize_func in optimization_steps:
                try:
                    current_result = optimize_func()
                    current_size = len(current_result)
                    
                    if current_size <= SLACK_STAMP_MAX_SIZE_BYTES:
                        return current_result
                    
                    # 次のステップに進む前にpygifsicleで最適化
                    if step_name != "標準最適化":
                        current_result = self.optimize_with_pygifsicle(current_result, "aggressive")
                        if len(current_result) <= SLACK_STAMP_MAX_SIZE_BYTES:
                            return current_result
                    
                except Exception as e:
                    print(f"{step_name}でエラー: {e}")
                    continue
            
            # すべての最適化を試しても128KBを超える場合
            final_result = self._ultra_optimize_for_slack(result)
            if len(final_result) > SLACK_STAMP_MAX_SIZE_BYTES:
                raise ValueError(f"Slackスタンプのサイズ制限（{SLACK_STAMP_MAX_SIZE_KB}KB）を超えています。"
                               f"現在のサイズ: {len(final_result) / 1024:.1f}KB\n"
                               f"元のファイルサイズが大きすぎるため、128KB以下に圧縮できませんでした。")
            
            return final_result
        
        else:
            raise ValueError("無効な最適化レベルです")
    
    def _force_optimize_for_slack(self, gif_bytes):
        """
        Slackスタンプ用の強制最適化
        
        Args:
            gif_bytes: 最適化するGIFのバイトデータ
        
        Returns:
            bytes: 最適化されたGIFのバイトデータ
        """
        from constants import SLACK_STAMP_SIZE, SLACK_STAMP_MAX_FRAMES, SLACK_STAMP_MAX_SIZE_BYTES
        
        # 新しいプロセッサーを作成
        temp_processor = GIFProcessor(gif_bytes)
        
        # フレーム数をさらに制限（20フレームまで）
        max_frames = min(SLACK_STAMP_MAX_FRAMES, SLACK_AGGRESSIVE_MAX_FRAMES)
        
        # より低い品質で再処理
        result = temp_processor.resize(
            SLACK_STAMP_SIZE, 
            SLACK_STAMP_SIZE, 
            optimize_for_slack=True, 
            max_frames=max_frames
        )
        
        return result
    
    def _ultra_optimize_for_slack(self, gif_bytes):
        """
        Slackスタンプ用の超強力最適化（最後の手段）
        
        Args:
            gif_bytes: 最適化するGIFのバイトデータ
        
        Returns:
            bytes: 最適化されたGIFのバイトデータ
        """
        from constants import SLACK_STAMP_SIZE, SLACK_STAMP_MAX_SIZE_BYTES
        
        try:
            # PILでGIFを開く
            gif = Image.open(io.BytesIO(gif_bytes))
            
            # 超強力最適化用の設定
            frames = []
            frame_index = 0
            max_frames = 10  # さらに少ないフレーム数
            
            # フレームを間引いて取得（1フレームおきに取得）
            while frame_index < max_frames:
                try:
                    gif.seek(frame_index * 2)  # 2フレームおきに取得
                    frame = gif.copy()
                    frame = frame.resize((SLACK_STAMP_SIZE, SLACK_STAMP_SIZE), Image.Resampling.LANCZOS)
                    
                    # 色数を削減（256色→64色）
                    frame = frame.quantize(colors=64, method=2)
                    
                    frames.append(frame)
                    frame_index += 1
                except EOFError:
                    break
            
            if not frames:
                # フレームが取得できない場合は最初のフレームのみ使用
                gif.seek(0)
                frame = gif.copy()
                frame = frame.resize((SLACK_STAMP_SIZE, SLACK_STAMP_SIZE), Image.Resampling.LANCZOS)
                frame = frame.quantize(colors=32, method=2)
                frames = [frame]
            
            # 超強力最適化で保存
            output = io.BytesIO()
            save_kwargs = {
                'format': 'GIF',
                'save_all': True,
                'append_images': frames[1:] if len(frames) > 1 else [],
                'duration': SLACK_AGGRESSIVE_DURATION,  # 30ms
                'loop': 0,
                'optimize': True,
                'quality': 1,  # 最低品質
                'transparency': 0,
                'disposal': 2,
            }
            
            frames[0].save(output, **save_kwargs)
            result = output.getvalue()
            
            # pygifsicleで最終最適化
            result = self.optimize_with_pygifsicle(result, "aggressive")
            
            return result
            
        except Exception as e:
            raise ValueError(f"超強力最適化中にエラーが発生しました: {str(e)}")
    
    def optimize_with_pygifsicle(self, gif_bytes, optimization_level="standard"):
        """
        pygifsicleを使用してGIFを最適化
        
        Args:
            gif_bytes: 最適化するGIFのバイトデータ
            optimization_level: 最適化レベル ("standard", "optimized", "aggressive")
        
        Returns:
            bytes: 最適化されたGIFのバイトデータ
        """
        if not PYGIFSICLE_AVAILABLE:
            return gif_bytes  # pygifsicleが利用できない場合は元のデータを返す
        
        try:
            # 一時ファイルにGIFを保存
            with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
                temp_file.write(gif_bytes)
                temp_file_path = temp_file.name
            
            # pygifsicleで最適化
            optimize_level = PYGIFSICLE_OPTIMIZATION_LEVELS.get(optimization_level, 1)
            optimize(temp_file_path, optimization_level=optimize_level)
            
            # 最適化されたファイルを読み込み
            with open(temp_file_path, 'rb') as optimized_file:
                optimized_bytes = optimized_file.read()
            
            # 一時ファイルを削除
            os.unlink(temp_file_path)
            
            return optimized_bytes
            
        except Exception as e:
            # エラーが発生した場合は元のデータを返す
            print(f"pygifsicle最適化エラー: {e}")
            return gif_bytes
    
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