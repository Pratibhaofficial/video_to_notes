import os
import numpy as np
import re
import time
from google import genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
client = genai.Client()

# ------------------ CHUNKING ------------------
def chunk_text(text, chunk_size=300):
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# ------------------ EMBEDDINGS ------------------
def create_embeddings(chunks):
    embeddings = []

    for chunk in chunks:
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=chunk
        )
        embeddings.append((chunk, response.embeddings[0].values))

    return embeddings


# ------------------ SIMILARITY ------------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def retrieve_relevant_chunks(query, embeddings, top_k=5):
    query_response = client.models.embed_content(
        model="gemini-embedding-2",
        contents=query
    )
    query_embedding = query_response.embeddings[0].values

    scores = []

    for chunk, emb in embeddings:
        score = cosine_similarity(query_embedding, emb)

        # keyword boost
        if "machine learning" in chunk.lower():
            score += 0.2

        scores.append((chunk, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [chunk for chunk, _ in scores[:top_k]]


# ------------------ ANSWER GENERATION ------------------
def generate_answer(query, context):
    prompt = f"""
You are a helpful AI tutor.

Answer the question using the context below.

- If relevant information exists, explain it clearly.
- Do NOT say "Not found" unless absolutely no related info is present.
- Answer like a teacher.

Context:
{context}

Question:
{query}
"""

    for _ in range(3):  # retry logic
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            print("Retrying...", e)
            time.sleep(3)

    return "Error: Unable to generate answer"


# ------------------ MAIN PIPELINE ------------------
def ask_question(query, transcript):
    chunks = chunk_text(transcript)

    embeddings = create_embeddings(chunks)

    relevant_chunks = retrieve_relevant_chunks(query, embeddings)

    # THIS is where joining happens (important)
    context = "\n\n".join(relevant_chunks)

    answer = generate_answer(query, context)

    return answer