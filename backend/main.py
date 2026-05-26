from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from moviepy import VideoFileClip

from ai.services.summarization import generate_notes
from ai.services.transcription import transcribe_audio, extract_audio
from ai.services.rag import ask_question

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    import time
    time.sleep(1)

    try:
        # 🎥 If video → use HER extract_audio
        if file.filename.lower().endswith(".mp4"):
            audio_path = file_path.replace(".mp4", ".mp3")
            extract_audio(file_path, audio_path)
        else:
            audio_path = file_path

        # 🎧 Use HER transcription
        transcript = transcribe_audio(audio_path)
        os.makedirs("transcripts", exist_ok=True)
        with open("transcripts/latest.txt", "w") as f:
            f.write(transcript)

        # 📝 Notes
        notes = generate_notes(transcript)

        return {
            "filename": file.filename,
            "transcript": transcript,
            "notes": notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/ask")
async def ask(query: str):

    if not query.strip():
        return {"error": "Empty query"}

    try:
        # 📂 Load transcript safely (FIXED)
        with open("transcripts/latest.txt", "r") as f:
            transcript = f.read()

    except FileNotFoundError:
        return {"error": "No transcript found. Please upload a file first."}

    answer = ask_question(query, transcript)
    return {
        "question": query,
        "answer": answer,
        "source": "lecture transcript"
    }