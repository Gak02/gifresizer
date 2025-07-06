"""
GIF Resizer メインアプリケーション
リファクタリング版
"""

import streamlit as st
from gif_processor import GIFProcessor
from ui_components import (
    render_file_upload,
    render_original_info,
    render_resize_settings,
    render_resize_result,
    render_sidebar,
    render_error_message
)
from utils import validate_file_size, adjust_size_for_aspect_ratio

def main():
    """メインアプリケーション"""
    # ページ設定
    st.set_page_config(
        page_title="GIF Resizer",
        page_icon="🎞️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎞️ GIF Resizer")
    st.write("GIFファイルをアップロードして、お好みのサイズにリサイズできます。")
    
    # セッション状態の初期化
    if 'uploaded_file_key' not in st.session_state:
        st.session_state.uploaded_file_key = None
    
    # ファイルアップロード
    uploaded_file = render_file_upload()
    
    if uploaded_file is not None:
        try:
            # ファイル情報を表示
            st.success(f"ファイル '{uploaded_file.name}' がアップロードされました！")
            
            # 元のGIFファイルのバイトデータを取得
            gif_bytes = uploaded_file.read()
            
            # ファイルサイズの検証
            is_valid, error_msg = validate_file_size(gif_bytes)
            if not is_valid:
                st.error(error_msg)
                return
                
        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {str(e)}")
            return
        
        try:
            # GIFプロセッサーを初期化
            processor = GIFProcessor(gif_bytes)
            info = processor.get_info()
            
            # 2カラムレイアウト
            col1, col2 = st.columns(2)
            
            with col1:
                render_original_info(processor)
            
            with col2:
                new_width, new_height, maintain_aspect, slack_optimization = render_resize_settings(
                    info['width'], 
                    info['height']
                )
            
            # リサイズ実行
            if st.button("🔄 リサイズ実行", type="primary"):
                try:
                    with st.spinner("GIFをリサイズしています..."):
                        # Slackスタンプ最適化が有効な場合
                        if slack_optimization:
                            st.info(f"🎯 Slackスタンプ用に最適化中... ({slack_optimization})")
                            try:
                                resized_gif_bytes = processor.create_slack_stamp(slack_optimization)
                                new_width = new_height = 128  # Slackスタンプサイズ
                                st.success("✅ Slackスタンプ最適化が完了しました！")
                            except ValueError as e:
                                st.error(f"Slackスタンプ最適化に失敗しました: {str(e)}")
                                st.info("💡 より軽量な最適化レベルを試してください")
                                return
                        else:
                            # アスペクト比を維持する場合の調整
                            if maintain_aspect:
                                new_width, new_height = adjust_size_for_aspect_ratio(
                                    new_width, new_height, 
                                    info['width'], info['height']
                                )
                            
                            # 通常のリサイズ
                            resized_gif_bytes = processor.resize(new_width, new_height)
                        
                        # 結果を表示
                        render_resize_result(
                            processor, 
                            resized_gif_bytes, 
                            new_width, 
                            new_height, 
                            info['file_size']
                        )
                        
                except Exception as e:
                    render_error_message(e)
                    
        except Exception as e:
            st.error(f"GIFファイルの処理中にエラーが発生しました: {str(e)}")
            st.write("ファイルが破損しているか、対応していない形式の可能性があります。")
    
    # サイドバーを表示
    render_sidebar()

if __name__ == "__main__":
    main()