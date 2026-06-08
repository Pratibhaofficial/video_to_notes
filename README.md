# Video to Notes

A full-stack AI application that converts lecture videos into structured notes and allows users to ask questions using a Retrieval-Augmented Generation (RAG) chatbot.

## What it does
- Extracts audio from uploaded video/audio files
- Transcribes speech into text using AI
- Generates structured notes from transcript
- Allows users to ask questions based on lecture content
- Uses RAG to ensure answers come from the lecture itself

## Features
- Video → Audio extraction
- Speech-to-text (Whisper)
- Automatic note generation
- AI chatbot 
- Semantic search using embeddings
- Simple frontend UI

## Project Structure

## Setup Instructions
### 1. Clone the repository
git clone <your-repo-url>
cd video_to_notes
### 2. Create a virtual environment
python -m venv venv
### 3. Activate the virtual environment
- On Windows:
  myenv\Scripts\activate
### 4. Install dependencies
pip install -r requirements.txt
### 5. Add environment variables
- Create .env file:
  GEMINI_API_KEY=your_api_key_here
### 6. Run backend
uvicorn backend.main:app --reload
### 7. Open frontend
- Open:
  frontend/index.html
  
## Week-wise Progress

| Week | Goal | Status |
| ------ | -------------------------------- | -------------- |
| Week 1 | Setup + basic AI understanding   | ✅ Done         |
| Week 2 | Audio extraction + transcription | ✅ Done         |
| Week 3 | Notes generation                 | ✅ Done         |
| Week 4 | RAG chatbot (core logic)         | ✅ Done         |
| Week 5 | Frontend + integration           | 🚧 In Progress |


## Team
- Khushi
- Pratibha

## Tech Stack
- Python
- FastAPI
- OpenAI Whisper
- Gemini API
- NumPy
- MoviePy
- HTML, CSS, JavaScript
