from moviepy import VideoFileClip
import whisper

model = whisper.load_model("base")

def extract_audio(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)
    return output_audio_path

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]

def clean_transcript(text):
    text = text.replace("\n", " ")
    return text.strip()