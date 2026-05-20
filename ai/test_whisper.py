from services.transcription import (
    extract_audio,
    transcribe_audio,
    clean_transcript
)

extract_audio("sample.mp4", "sample.mp3")

text = transcribe_audio("sample.mp3")

cleaned = clean_transcript(text)

print(cleaned)