from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from moviepy import VideoFileClip
from pydantic import BaseModel

from ai.services.youtube import download_youtube_audio
from ai.services.summarization import generate_notes
from ai.services.transcription import transcribe_audio, extract_audio
from ai.services.rag import ask_question
import uuid
class AskRequest(BaseModel):
    session_id: str
    query: str
sessions = {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "transcripts", "latest.txt")
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)


@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global sessions

    allowed_extensions = (".mp4", ".mp3", ".wav", ".mkv", ".m4a")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload .mp4, .mp3, .wav, .mkv, or .m4a"
        )

    # ✅ ensure folder exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = file.filename.split(".")[-1]
    safe_filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    print("Saving file at:", file_path)

    # ✅ save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print("File save error:", str(e))
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")

    try:
        # ✅ process file
        if ext == "mp4":
            audio_path = file_path.replace(".mp4", ".mp3")
            extract_audio(file_path, audio_path)
        else:
            audio_path = file_path

        print("Audio path:", audio_path)

        transcript, detected_lang = transcribe_audio(audio_path)

        if not transcript or transcript.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Could not extract speech from this file."
            )

        # ✅ create session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "transcript": transcript,
            "history": []
        }

        # ✅ save transcript
        os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)
        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(transcript)

        # ✅ generate notes
        try:
            notes = generate_notes(transcript)
        except Exception:
            notes = "Notes could not be generated."

        # ✅ RETURN RESPONSE (this was missing)
        return {
            "session_id": session_id,
            "filename": file.filename,
            "transcript": transcript,
            "notes": notes
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Processing error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(req: AskRequest):
    session_id = req.session_id
    query = req.query
    # 🔹 Validate input
    if not query.strip():
        return {"error": "Empty query. Please enter a question."}

    # 🔹 Check session exists
    if session_id not in sessions:
        return {"error": "Invalid session_id"}

    try:
        transcript = sessions[session_id]["transcript"]

        answer = ask_question(query, transcript)

        # 🔥 Save chat history
        sessions[session_id]["history"].append({
            "question": query,
            "answer": answer
        })

        return {
            "question": query,
            "answer": answer
        }

    except Exception as e:
        return {
            "error": "AI service is busy. Try again.",
            "details": str(e)
        }
        
        

@app.post("/upload-youtube")
async def upload_youtube(url: str):
    global sessions

    if not url.strip():
        raise HTTPException(status_code=400, detail="Please provide a YouTube URL.")
    
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL.")
    
    try:
        audio_path = download_youtube_audio(url)

        transcript, detected_lang = transcribe_audio(audio_path)

        if not transcript or transcript.strip() == "":
            raise HTTPException(status_code=422, detail="Could not extract speech.")

        # ✅ CREATE SESSION ONLY AFTER SUCCESS
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "transcript": transcript,
            "history": []
        }

        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(transcript)

        try:
            notes = generate_notes(transcript)
        except Exception:
            notes = "Notes could not be generated."

        return {
            "session_id": session_id,
            "url": url,
            "transcript": transcript,
            "notes": notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))