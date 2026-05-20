from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from services.transcription import transcribe_audio
app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = [".mp4", ".mp3", ".wav"]

def is_valid_file(filename):
   return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)

@app.get("/")
def home():
    return {"message": "Server is running 🚀"}
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not is_valid_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        from services.transcription import transcribe_audio

        transcript = transcribe_audio(file_path)

        return {
            "filename": file.filename,
            "transcript": transcript
        }

    except Exception as e:
        return {"error": str(e)}