from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from moviepy import VideoFileClip

from ai.services.summarization import generate_notes
from ai.services.transcription import transcribe_audio, extract_audio

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 🎥 If video → use HER extract_audio
        if file.filename.lower().endswith(".mp4"):
            audio_path = file_path.replace(".mp4", ".mp3")
            extract_audio(file_path, audio_path)
        else:
            audio_path = file_path

        # 🎧 Use HER transcription
        transcript = transcribe_audio(audio_path)

        # 📝 Notes
        notes = generate_notes(transcript)

        return {
            "filename": file.filename,
            "transcript": transcript,
            "notes": notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))