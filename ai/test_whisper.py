from services.transcription import (
    extract_audio,
    transcribe_audio,
    clean_transcript
)
if __name__ == "__main__":
    # Step 1: Extract audio
    extract_audio("sample.mp4", "sample.mp3")
    
    # Step 2: Transcribe
    text = transcribe_audio("sample.mp3")
    
    # Step 3: Clean transcript
    cleaned = clean_transcript(text)
    
    print(cleaned)