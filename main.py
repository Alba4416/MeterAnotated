from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import cv2
from ultralytics import YOLO
import os
import subprocess

app = FastAPI()

# FFmpegのパスを指定
ffmpeg_path = r"C:\Users\keiei\AppData\Local\Programs\ffmpeg-master-latest-win64-gpl-shared\bin\ffmpeg.exe"

def convert_to_h264(input_path, output_path):
    command = [
        ffmpeg_path,
        '-i', input_path,
        '-vcodec', 'libx264',
        '-crf', '23',
        '-preset', 'fast',
        output_path
    ]
    subprocess.run(command, check=True)

@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    # ファイルを受け取り、必要な処理を行う
    contents = await file.read()
    input_path = "uploaded_video.mp4"
    output_path = "annotated_video.mp4"
    temp_output_path = "temp_annotated_video.avi"

    try:
        with open(input_path, "wb") as f:
            f.write(contents)
        print(f"Received file: {input_path}")

        # 動画処理
        try:
            model = YOLO('C:\\Users\\keiei\\myproject\\MeterReading\\best.pt')  # YOLOモデルのパスを指定
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            return JSONResponse(content={"message": "Error loading model."}, status_code=500)

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print("Error opening video file.")
            return JSONResponse(content={"message": "Error opening video file."}, status_code=500)

        annotated_frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                results = model.track(frame, persist=True)
                annotated_frame = results[0].plot()
                annotated_frames.append(annotated_frame)
            else:
                break
        cap.release()
        print("Video processing complete.")

        # 変換後の動画を一時ファイルとして保存
        if annotated_frames:
            height, width, layers = annotated_frames[0].shape
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # XVIDコーデックを使用
            video = cv2.VideoWriter(temp_output_path, fourcc, 30, (width, height))
            for frame in annotated_frames:
                video.write(frame)
            video.release()
            print(f"Temporary annotated video saved to: {temp_output_path}")

            # FFmpegを使用してH264に変換
            convert_to_h264(temp_output_path, output_path)
            print(f"Annotated video converted to H264 and saved to: {output_path}")
        else:
            print("No frames processed.")
            return JSONResponse(content={"message": "No frames processed."}, status_code=500)

        return FileResponse(output_path, media_type='video/mp4')

    except Exception as e:
        print(f"Unhandled error: {e}")
        return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)








