import streamlit as st
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import uvicorn
from threading import Thread
import requests
import os

# FastAPIアプリケーションの設定
app = FastAPI()

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    file_location = f"temp_files/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # ここで動画の変換処理を行う
    # 仮に、変換後の動画を annotated_video.mp4 として保存すると仮定
    annotated_video_path = "temp_files/annotated_video.mp4"
    # ダミー処理としてアップロードされたファイルをコピー
    with open(annotated_video_path, "wb") as f:
        f.write(open(file_location, "rb").read())

    return FileResponse(annotated_video_path)

def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8000)

# スレッドでFastAPIサーバーを起動
api_thread = Thread(target=run_api)
api_thread.start()

# Streamlitアプリケーションの設定
st.title("動画アップロードアプリ")

uploaded_file = st.file_uploader("動画をアップロードしてください", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    local_uploaded_path = "uploaded_video.mp4"
    with open(local_uploaded_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    
    st.video(local_uploaded_path)

    files = {"file": open(local_uploaded_path, "rb")}
    
    try:
        response = requests.post("http://127.0.0.1:8000/upload-video/", files=files)
        
        if response.status_code == 200:
            st.success("ファイルが正常にアップロードされ、変換されました。")
            
            annotated_video_path = "annotated_video.mp4"
            
            with open(annotated_video_path, "wb") as f:
                f.write(response.content)
            
            with open(annotated_video_path, "rb") as f:
                video_bytes = f.read()

            st.video(video_bytes)
        else:
            st.error(f"ファイルのアップロードに失敗しました。ステータスコード: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"接続エラーが発生しました: {e}")


