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
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(file_path, language=None):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    result = get_model().transcribe(
        file_path,
        task="transcribe",  # transcribe in original language
        language=language   # None = auto detect, "hi" = Hindi, "fr" = French etc.
    )
    
    detected_language = result.get("language", "unknown")
    print(f"[Transcription] Detected language: {detected_language}")
    
    return result["text"], detected_language

def clean_transcript(text):
    text = text.replace("\n", " ")
    return text.strip()