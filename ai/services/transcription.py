from moviepy import VideoFileClip
import whisper
import os

model = whisper.load_model("base")

def extract_audio(video_path, output_audio_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)
    video.close()
    return output_audio_path

def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    result = model.transcribe(file_path)
    return result["text"]

def clean_transcript(text):
    text = text.replace("\n", " ")
    return text.strip()