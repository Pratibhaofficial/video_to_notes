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
    allow_origins=["*"],
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
    global sessions


    allowed_extensions = (".mp4", ".mp3", ".wav", ".mkv", ".m4a")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload .mp4, .mp3, .wav, .mkv, or .m4a"
        )

    file_path = os.path.abspath(os.path.join(UPLOAD_DIR, file.filename))

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.lower().endswith(".mp4"):
            audio_path = file_path.replace(".mp4", ".mp3")
            extract_audio(file_path, audio_path)
        else:
            audio_path = file_path

        transcript, detected_lang = transcribe_audio(audio_path)
        print(f"Detected language: {detected_lang}")

        if not transcript or transcript.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Could not extract speech from this file. Check if the audio is clear."
            )
        session_id = str(uuid.uuid4())

        sessions[session_id] = {
        "transcript": transcript,
        "history": []
        }
        os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)
        with open(TRANSCRIPT_PATH, "w", encoding="utf-8") as f:
            f.write(transcript)

        print("Saved transcript at:", TRANSCRIPT_PATH)
        print("Transcript preview:", transcript[:200])

        try:
            notes = generate_notes(transcript)
        except Exception:
            notes = "Notes could not be generated. Transcript is available above."

        return {
            "session_id": session_id,
            "filename": file.filename,
            "transcript": transcript,
            "notes": notes
        }

    except HTTPException:
        raise

    except Exception as e:
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