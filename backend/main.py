from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from moviepy import VideoFileClip

from ai.services.summarization import generate_notes
from ai.services.transcription import transcribe_audio, extract_audio
from ai.services.rag import ask_question
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "transcripts", "latest.txt")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = "uploads"
os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)


@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 🎥 If video → extract audio
        if file.filename.lower().endswith(".mp4"):
            audio_path = file_path.replace(".mp4", ".mp3")
            extract_audio(file_path, audio_path)
        else:
            audio_path = file_path

        # 🎧 Transcription
        transcript = transcribe_audio(audio_path)
        os.makedirs("transcripts", exist_ok=True)
        with open("transcripts/latest.txt", "w") as f:
            f.write(transcript)

        # ✅ SAVE TRANSCRIPT HERE (CORRECT PLACE)
        os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)

        with open(TRANSCRIPT_PATH, "w") as f:
            f.write(transcript)

        print("Saved transcript at:", TRANSCRIPT_PATH)
        print("Transcript preview:", transcript[:200])

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
        with open(TRANSCRIPT_PATH, "r") as f:
            transcript = f.read()
        print("Reading transcript from:", TRANSCRIPT_PATH)

    except FileNotFoundError:
        return {
            "error": "No transcript found. Please upload a file first using /upload endpoint."
        }

    try:
        answer = ask_question(query, transcript)

        return {
            "question": query,
            "answer": answer,
            "source": "lecture transcript"
        }

    except Exception as e:
        return {
            "error": "AI service is busy. Try again.",
            "details": str(e)
        }
    
from ai.services.youtube import download_youtube_audio

@app.post("/upload-youtube")
async def upload_youtube(url: str):
    if not url.strip():
        raise HTTPException(status_code=400, detail="Please provide a YouTube URL.")
    
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
    
    try:
        # Download audio from YouTube
        audio_path = download_youtube_audio(url)
        
        # Transcribe
        transcript = transcribe_audio(audio_path)
        
        if not transcript or transcript.strip() == "":
            raise HTTPException(status_code=422, detail="Could not extract speech from this video.")
        
        # Save transcript
        os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)
        with open(TRANSCRIPT_PATH, "w") as f:
            f.write(transcript)
        
        # Generate notes
        try:
            notes = generate_notes(transcript)
        except Exception:
            notes = "Notes could not be generated. Transcript is available above."
        
        return {
            "url": url,
            "transcript": transcript,
            "notes": notes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))