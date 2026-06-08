import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_notes(transcript: str) -> str:
    # Guard — empty transcript
    if not transcript or transcript.strip() == "":
        return "No transcript available to generate notes."

    prompt = f"""
You are an expert academic note-maker.
Convert the following lecture transcript into well-structured notes.

STRICT RULES:
- Use ONLY information from the transcript — do NOT add outside knowledge
- If something is unclear in the transcript, skip it
- Remove all filler words and repetition
- Keep it concise and exam-friendly

Output format (use this EXACTLY):

# [Lecture Title]

## Main Topics
- topic 1
- topic 2

## Detailed Notes

### [Sub-topic 1]
- point
- point

### [Sub-topic 2]
- point
- point

## Key Takeaways
- takeaway 1
- takeaway 2

## Summary
2-3 sentence summary of the entire lecture.

Transcript:
{transcript}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"[Attempt {attempt + 1} failed] {e}")
            if attempt < 2:
                time.sleep(5)

    return "Failed to generate notes after 3 attempts. Please try again later."


def chunk_text(text, size=1000):
    chunks = [text[i:i+size] for i in range(0, len(text), size)]
    return chunks


def generate_notes_for_long_transcript(transcript):
    chunks = chunk_text(transcript)
    all_notes = []

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1} of {len(chunks)}...")
        notes = generate_notes(chunk)
        all_notes.append(notes)

    combined = "\n\n---\n\n".join(all_notes)
    return combined