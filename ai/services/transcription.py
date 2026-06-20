from moviepy import VideoFileClip
import whisper
import os


def extract_audio(video_path, output_audio_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)
    video.close()
    
    return output_audio_path


_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")  # keep base for speed
    return _model


def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    model = get_model()

    # 🔥 STEP 1: Try Hindi bias (best for Hinglish)
    result = model.transcribe(
        file_path,
        task="transcribe",
        language="hi"
    )

    text = result["text"]

    # 🔥 STEP 2: Check if it's actually English
    # (simple heuristic)
    ascii_ratio = sum(c.isascii() for c in text) / len(text)

    if ascii_ratio > 0.95:
        print("[Transcription] Detected mostly English → retrying with English")

        result = model.transcribe(
            file_path,
            task="transcribe",
            language="en"
        )

    detected_language = result.get("language", "unknown")
    print(f"[Transcription] Final language: {detected_language}")

    return result["text"], detected_language


def clean_transcript(text):
    text = text.replace("\n", " ")
    return text.strip()