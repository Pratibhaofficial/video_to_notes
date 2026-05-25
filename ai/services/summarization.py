import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_notes(transcript):
    prompt = f"""
You are an expert academic note-maker.
Convert the following lecture transcript into well-structured notes.

Requirements:
- Use headings and subheadings
- Use bullet points
- Highlight key concepts
- Remove repetition
- Keep it concise and exam-friendly

Output format:
1. Title
2. Main Topics
3. Detailed Notes
4. Key Takeaways

Transcript:
{transcript}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

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