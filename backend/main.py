from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from moviepy import VideoFileClip

from ai.services.summarization import generate_notes
from ai.services.transcription import transcribe_audio, extract_audio
from ai.services.rag import ask_question

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPT_PATH = os.path.join(BASE_DIR, "transcripts", "latest.txt")
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)


@app.get("/")
def home():
    return {"message": "Server is running 🚀"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

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

        transcript = transcribe_audio(audio_path)

        if not transcript or transcript.strip() == "":
            raise HTTPException(
                status_code=422,
                detail="Could not extract speech from this file. Check if the audio is clear."
            )

        os.makedirs(os.path.dirname(TRANSCRIPT_PATH), exist_ok=True)
        with open(TRANSCRIPT_PATH, "w") as f:
            f.write(transcript)

        print("Saved transcript at:", TRANSCRIPT_PATH)
        print("Transcript preview:", transcript[:200])

        try:
            notes = generate_notes(transcript)
        except Exception:
            notes = "Notes could not be generated. Transcript is available above."

        return {
            "filename": file.filename,
            "transcript": transcript,
            "notes": notes
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask(query: str):

    if not query.strip():
        return {"error": "Empty query. Please enter a question."}

    try:
        with open(TRANSCRIPT_PATH, "r") as f:
            transcript = f.read()
        print("Reading transcript from:", TRANSCRIPT_PATH)

    except FileNotFoundError:
        return {
            "error": "No transcript found. Please upload a file first."
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