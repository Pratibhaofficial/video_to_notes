import os
import time
import numpy as np
from google import genai
from dotenv import load_dotenv

# ─── SETUP ───────────────────────────────────────────────────────────────────

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
dotenv_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=dotenv_path)

api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(f"Could not find an API key in your .env file at: {dotenv_path}")

client = genai.Client(
    api_key=api_key,
    http_options={"api_version": "v1beta"}
)

# ─── CACHE ───────────────────────────────────────────────────────────────────

_cached_embeddings = None
_cached_transcript = None

# ─── STEP 2: CHUNK TRANSCRIPT ────────────────────────────────────────────────

def chunk_text(text, chunk_size=400, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# ─── STEP 3: CREATE EMBEDDINGS ───────────────────────────────────────────────

def create_embeddings(chunks):
    embeddings = []
    for i, chunk in enumerate(chunks):
        try:
            response = client.models.embed_content(
                model="models/gemini-embedding-2",  # fixed from models/gemini-embedding-2
                contents=chunk
            )
            embeddings.append((chunk, response.embeddings[0].values))
        except Exception as e:
            print(f"Warning: Skipping chunk {i} due to error: {e}")
    return embeddings

# ─── STEP 4: SIMILARITY SEARCH ───────────────────────────────────────────────

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_relevant_chunks(query, embeddings, top_k=5, min_score=0.25):
    try:
        response = client.models.embed_content(
            model="models/gemini-embedding-2",
            contents=query
        )
        query_embedding = response.embeddings[0].values
    except Exception as e:
        print(f"Error embedding query: {e}")
        return [], 0.0

    scores = []
    for chunk, emb in embeddings:
        score = cosine_similarity(query_embedding, emb)
        scores.append((chunk, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    # ← NEW: if best score is too low, question is out of scope
    top_score = scores[0][1] if scores else 0.0
    if top_score < min_score:
        return [], top_score

    return [chunk for chunk, score in scores[:top_k] if score >= min_score], top_score

# ─── STEP 5: GENERATE ANSWER ─────────────────────────────────────────────────

def generate_answer(query, context):
    if not context.strip():
        return "This wasn't covered in the lecture."

    prompt = f"""
You are a helpful AI tutor.
Answer ONLY from the context below.

Format your answer EXACTLY like this:

**Definition:**
(one line definition)

**Explanation:**
(2-3 bullet points explaining the concept)

**Example (if available in context):**
(a real example from the lecture, or skip if not present)

Rules:
- Use ONLY the context provided
- Never add outside knowledge
- If not found, say: "This wasn't covered in the lecture."

Context:
{context}

Question: {query}
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

    return "AI service is busy. Please try again."

# ─── STEP 6: MAIN PIPELINE ───────────────────────────────────────────────────

def ask_question(query, transcript):
    global _cached_embeddings, _cached_transcript

    if not query.strip():
        return "Please enter a valid question."

    if not transcript.strip():
        return "No transcript available."

    if _cached_embeddings is None or _cached_transcript != transcript:
        print("Computing embeddings...")
        chunks = chunk_text(transcript)
        _cached_embeddings = create_embeddings(chunks)
        _cached_transcript = transcript
        print(f"Done. {len(_cached_embeddings)} chunks embedded.")

    # ← updated to unpack tuple
    relevant_chunks, top_score = retrieve_relevant_chunks(query, _cached_embeddings)

    if not relevant_chunks:
        return "This wasn't covered in the lecture."

    context = "\n\n".join(relevant_chunks)
    return generate_answer(query, context)