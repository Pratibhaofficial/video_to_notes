from services.transcription import transcribe_audio

text = transcribe_audio("sample.mp3")

print(text)