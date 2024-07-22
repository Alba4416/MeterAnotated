import streamlit as st
import requests
import os

st.title("動画アップロードアプリ")

uploaded_file = st.file_uploader("動画をアップロードしてください", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # ローカルにアップロードされた動画を保存する
    local_uploaded_path = "uploaded_video.mp4"
    with open(local_uploaded_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # アップロードされた動画を再生する
    st.video(local_uploaded_path)

    # 動画をFastAPIサーバーに送信する
    files = {"file": uploaded_file.getvalue()}
    response = requests.post("http://127.0.0.1:8000/upload-video/", files=files)

    if response.status_code == 200:
        st.success("ファイルが正常にアップロードされ、変換されました。")
        
        # 変換後の動画ファイルを一時的に保存する
        annotated_video_path = "annotated_video.mp4"
        
        with open(annotated_video_path, "wb") as f:
            f.write(response.content)
        
        # 変換後の動画をバイナリデータとして読み込む
        with open(annotated_video_path, "rb") as f:
            video_bytes = f.read()

        # 変換後の動画ファイルを再生する
        st.video(video_bytes)
    else:
        st.error("ファイルのアップロードに失敗しました。")

