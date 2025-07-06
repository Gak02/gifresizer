"""
UIコンポーネント
"""

import streamlit as st
from constants import (
    RESIZE_METHODS, 
    PRESET_SIZES, 
    SLACK_STAMP_PRESETS,
    MIN_SCALE_PERCENT, 
    MAX_SCALE_PERCENT, 
    DEFAULT_SCALE_PERCENT,
    MIN_IMAGE_SIZE,
    MAX_IMAGE_SIZE
)
from utils import (
    calculate_aspect_ratio, 
    adjust_size_for_aspect_ratio,
    format_file_size,
    calculate_size_change,
    create_download_filename
)

def render_file_upload():
    """ファイルアップロードUIを表示"""
    return st.file_uploader(
        "GIFファイルを選択してください", 
        type=['gif'],
        help="GIF形式のファイルのみアップロード可能です。",
        key="gif_uploader"
    )

def render_original_info(processor):
    """元のGIF情報を表示"""
    info = processor.get_info()
    
    st.subheader("📊 元のGIF情報")
    st.write(f"**幅:** {info['width']} px")
    st.write(f"**高さ:** {info['height']} px")
    st.write(f"**フレーム数:** {info['frame_count']}")
    st.write(f"**ファイルサイズ:** {format_file_size(info['file_size'])}")
    st.write(f"**フレーム間隔:** {info['duration']} ms")
    
    # 元のGIFを表示
    st.image(processor.gif_bytes, caption="元のGIF", width=200)

def render_resize_settings(original_width, original_height):
    """リサイズ設定UIを表示"""
    st.subheader("🎛️ リサイズ設定")
    
    # サイズ指定方法の選択
    resize_method = st.radio(
        "リサイズ方法を選択:",
        RESIZE_METHODS
    )
    
    new_width = new_height = None
    slack_optimization = None
    
    if resize_method == "カスタムサイズ":
        new_width = st.number_input(
            "新しい幅 (px)", 
            min_value=MIN_IMAGE_SIZE, 
            max_value=MAX_IMAGE_SIZE, 
            value=original_width,
            step=10
        )
        new_height = st.number_input(
            "新しい高さ (px)", 
            min_value=MIN_IMAGE_SIZE, 
            max_value=MAX_IMAGE_SIZE, 
            value=original_height,
            step=10
        )
        
    elif resize_method == "比率指定":
        scale_percent = st.slider(
            "スケール (%)", 
            min_value=MIN_SCALE_PERCENT, 
            max_value=MAX_SCALE_PERCENT, 
            value=DEFAULT_SCALE_PERCENT,
            step=5
        )
        new_width = int(original_width * scale_percent / 100)
        new_height = int(original_height * scale_percent / 100)
        st.write(f"新しいサイズ: {new_width} × {new_height} px")
        
    else:  # プリセットサイズ
        # 通常のプリセットサイズ
        preset = st.selectbox(
            "プリセットサイズを選択:",
            PRESET_SIZES
        )
        new_width, new_height = map(int, preset.split('x'))
        st.write(f"選択されたサイズ: {new_width} × {new_height} px")
    
    # Slackスタンプ専用オプション
    if st.checkbox("🎯 Slackスタンプ用に最適化", value=False):
        st.info("Slackスタンプ用の最適化を適用します（128×128px、128KB以下、50フレーム以下）")
        slack_preset = st.selectbox(
            "Slackスタンプ最適化レベル:",
            SLACK_STAMP_PRESETS
        )
        
        if slack_preset == "Slackスタンプ (128×128)":
            slack_optimization = "standard"
        elif slack_preset == "Slackスタンプ 最適化 (128×128, 50フレーム以下)":
            slack_optimization = "optimized"
        elif slack_preset == "Slackスタンプ 軽量 (128×128, 128KB以下)":
            slack_optimization = "lightweight"
        
        # サイズを128×128に固定
        new_width = new_height = 128
        st.success("✅ Slackスタンプ用に128×128pxに設定されました")
    
    # アスペクト比を維持するオプション
    maintain_aspect = st.checkbox(
        "アスペクト比を維持", 
        value=True,
        help="チェックすると、元の画像の縦横比を保持します。"
    )
    
    if maintain_aspect and resize_method == "カスタムサイズ":
        aspect_ratio = calculate_aspect_ratio(original_width, original_height)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("幅に合わせて高さを調整"):
                new_height = int(new_width / aspect_ratio)
                st.rerun()
        
        with col2:
            if st.button("高さに合わせて幅を調整"):
                new_width = int(new_height * aspect_ratio)
                st.rerun()
    
    return new_width, new_height, maintain_aspect, slack_optimization

def render_resize_result(processor, resized_gif_bytes, new_width, new_height, original_size):
    """リサイズ結果を表示"""
    st.success("✅ リサイズが完了しました！")
    
    # リサイズ後の情報を表示
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("📈 リサイズ後の情報")
        st.write(f"**新しい幅:** {new_width} px")
        st.write(f"**新しい高さ:** {new_height} px")
        st.write(f"**新しいファイルサイズ:** {format_file_size(len(resized_gif_bytes))}")
        
        # ファイルサイズの変化を表示
        size_change = calculate_size_change(original_size, len(resized_gif_bytes))
        if size_change > 0:
            st.write(f"**サイズ変化:** +{size_change:.1f}% 📈")
        else:
            st.write(f"**サイズ変化:** {size_change:.1f}% 📉")
        
        # Slackスタンプ適合性チェック
        from constants import SLACK_STAMP_SIZE, SLACK_STAMP_MAX_SIZE_BYTES, SLACK_STAMP_MAX_FRAMES
        
        if new_width == SLACK_STAMP_SIZE and new_height == SLACK_STAMP_SIZE:
            st.write("🎯 **Slackスタンプ適合性:**")
            
            # サイズチェック
            if len(resized_gif_bytes) <= SLACK_STAMP_MAX_SIZE_BYTES:
                st.write("✅ ファイルサイズ: 128KB以下")
            else:
                st.write(f"❌ ファイルサイズ: {len(resized_gif_bytes) / 1024:.1f}KB (128KB超過)")
            
            # フレーム数チェック
            frame_count = processor.get_frame_count()
            if frame_count <= SLACK_STAMP_MAX_FRAMES:
                st.write("✅ フレーム数: 50フレーム以下")
            else:
                st.write(f"❌ フレーム数: {frame_count}フレーム (50フレーム超過)")
            
            # 総合判定
            if (len(resized_gif_bytes) <= SLACK_STAMP_MAX_SIZE_BYTES and 
                frame_count <= SLACK_STAMP_MAX_FRAMES):
                st.success("🎉 **Slackスタンプとして使用可能です！**")
            else:
                st.warning("⚠️ **Slackスタンプ用に最適化が必要です**")
                st.info("💡 **軽量最適化**を選択すると、より強力な最適化が適用されます")
    
    with col4:
        st.subheader("🎞️ リサイズ後のGIF")
        st.image(resized_gif_bytes, caption="リサイズ後のGIF", width=200)
    
    # ダウンロードボタン
    download_filename = create_download_filename(
        processor.original_gif.filename or "gif", 
        new_width, 
        new_height
    )
    
    st.download_button(
        label="📥 リサイズされたGIFをダウンロード",
        data=resized_gif_bytes,
        file_name=download_filename,
        mime="image/gif",
        type="primary"
    )

def render_sidebar():
    """サイドバーを表示"""
    with st.sidebar:
        st.header("📖 使用方法")
        st.write("""
        1. **GIFファイルをアップロード**
           - 対応形式: .gif
           
        2. **リサイズ方法を選択**
           - カスタムサイズ: 幅と高さを個別指定
           - 比率指定: パーセンテージで指定
           - プリセットサイズ: 定型サイズから選択
           
        3. **Slackスタンプ最適化**
           - 🎯 チェックボックスで有効化
           - 3段階の最適化レベルから選択
           
        4. **リサイズ実行**
           - 処理完了後、ダウンロード可能
        """)
        
        st.header("🎯 Slackスタンプ機能")
        st.write("""
        **Slackスタンプ要件:**
        - サイズ: 128×128px
        - ファイルサイズ: 128KB以下
        - フレーム数: 50フレーム以下
        
        **最適化レベル:**
        - 標準: 128×128pxのみ
        - 最適化: +50フレーム制限
        - 軽量: +128KB以下保証
        """)
        
        st.header("💡 ヒント")
        st.write("""
        - アスペクト比を維持することで、画像の歪みを防げます
        - Slackスタンプ用最適化で自動的に要件を満たします
        - 大きなGIFは軽量最適化を選択してください
        """)

def render_error_message(error):
    """エラーメッセージを表示"""
    st.error(f"❌ エラーが発生しました: {str(error)}")
    st.write("**対処法:**")
    st.write("- ファイルが正常なGIF形式か確認してください")
    st.write("- ファイルサイズが200MB以下か確認してください")
    st.write("- ブラウザを更新して再度お試しください") 