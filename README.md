# 🎥 Video to Notes (AI + RAG)

A full-stack AI application that converts lecture videos into structured notes and enables intelligent question-answering using a Retrieval-Augmented Generation (RAG) pipeline.

---

## ✨ What it does

- Extracts audio from uploaded video/audio files or YouTube links  
- Transcribes speech into text using Whisper  
- Generates structured, exam-ready notes  
- Allows users to ask questions based on lecture content  
- Uses RAG to ensure accurate, context-based answers  

---

## 🧠 Key Features

-  Video/Audio → Text transcription (Whisper)  
-  Automatic note generation (LLM)  
-  Chat with lecture (context-aware Q&A)  
-  RAG pipeline using chunking + embeddings  
-  Session-based chat history  
-  YouTube video support  
-  Clean frontend UI  

---

## ⚙️ How RAG Works (Core Highlight)

1. Transcript is split into smaller chunks  
2. Each chunk is converted into embeddings  
3. User query is also embedded  
4. Relevant chunks are retrieved using similarity search  
5. LLM generates answers ONLY from retrieved context  

👉 This ensures:
- No hallucination  
- Answers stay grounded in lecture  
- Higher accuracy than normal chatbots  

---

## 🏗️ Project Structure

video-to-notes/

├── backend/  
│   ├── main.py  

├── ai/  
│   ├── transcription.py  
│   ├── summarization.py  
│   ├── rag.py  
│   └── youtube.py  

├── frontend/  
│   ├── index.html  
│   ├── style.css  
│   └── script.js  

├── uploads/  
├── transcripts/  
└── README.md  

---

## 🛠️ Setup Instructions

### 1. Clone the repository
git clone <your-repo-url>  
cd video_to_notes  

### 2. Create virtual environment
python -m venv venv  

### 3. Activate environment
Windows:
venv\Scripts\activate  

### 4. Install dependencies
pip install -r requirements.txt  

### 5. Add environment variables
Create a `.env` file:
GEMINI_API_KEY=your_api_key_here  

### 6. Run backend
uvicorn backend.main:app --reload  

### 7. Run frontend
Open:
frontend/index.html  

---

## 📅 Week-wise Progress

| Week | Goal | Status |
|------|------|--------|
| Week 1 | Setup + AI basics | ✅ Done |
| Week 2 | Transcription (Whisper) | ✅ Done |
| Week 3 | Notes generation | ✅ Done |
| Week 4 | RAG chatbot (embeddings + retrieval) | ✅ Done |
| Week 5 | Frontend + integration | ✅ Done |
| Week 6 | Chat history + YouTube support | ✅ Done |

---

## 👩‍💻 Tech Stack

- Backend: FastAPI, Python  
- AI: Whisper, Gemini API  
- RAG: Embeddings + similarity search  
- Processing: MoviePy  
- Frontend: HTML, CSS, JavaScript  

---

## 👥 Team

- Khushi  
- Pratibha  


