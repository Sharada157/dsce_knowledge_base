# DSCE RAG Chatbot

An intelligent, context-aware Retrieval-Augmented Generation (RAG) assistant for **Dayananda Sagar College of Engineering (DSCE)**, Bengaluru.

This is an unofficial student project designed to provide instant answers to college admissions, fee structures, academic calendars, examinations, campus facilities, placements, and campus life queries using verified public documents and student-contributed insights.

---

## Architecture Overview

```
[User Query]
     │
     ▼
[Plain HTML/JS Chat Widget]
     │
     ▼
[FastAPI Backend] ──> [ChromaDB Vector Store] (all-MiniLM-L6-v2 embeddings)
     │                        │
     ▼                        ▼
[LLM (Groq LPUs / Gemini)] <── [Retrieved Chunks + Source URLs]
     │
     ▼
[Response with Verified Citations + Suggested Questions]
```

## Tech Stack
- **Vector Database:** ChromaDB (persistent local vector storage)
- **Embeddings:** `all-MiniLM-L6-v2` via `sentence-transformers`
- **Primary LLM:** Groq API (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`) – Sub-2 second generation
- **Secondary LLM:** Google Gemini API (`gemini-3.5-flash-lite`)
- **Backend:** FastAPI (Python 3.11) with CORS & streaming support
- **Frontend:** Responsive vanilla HTML/CSS/JavaScript with Marked.js
- **Data Sources:** 17 official DSCE circulars & 40 peer student Q&As

---

## Quick Start (Run Locally)

### 1. Clone & Set Up Environment
```powershell
git clone https://github.com/Sharada157/dsce_knowledge_base.git
cd dsce_knowledge_base
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy the example environment template and add your Groq or Gemini API key:
```powershell
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY or GEMINI_API_KEY
```

### 3. Ingest Knowledge Base
```powershell
python ingest.py
```

### 4. Start the Server
```powershell
uvicorn main:app --reload --port 8000
```
Open your browser at **[http://127.0.0.1:8000](http://127.0.0.1:8000)** to test the chatbot!
Explore interactive OpenAPI docs at **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

---

## Cloud Deployment (Day 3)

### Option A: Free Deployment on Render
1. Push your code to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) &rarr; **New +** &rarr; **Blueprint**.
3. Select your repository `dsce_knowledge_base`. Render will automatically detect `render.yaml`.
4. Enter your `GROQ_API_KEY` and/or `GEMINI_API_KEY` when prompted in the environment variables form.
5. Click **Apply** to deploy.

### Option B: Docker Container
Build and run anywhere with Docker:
```bash
docker build -t dsce-rag-chatbot .
docker run -p 8000:8000 -e GROQ_API_KEY="your_key" dsce-rag-chatbot
```

## Project Structure
```
dsce_knowledge_base/
├── dsce_knowledge_base/       # Curated Markdown knowledge base
│   ├── 01_admissions/         # Fee structures (KEA, COMEDK, Management, PG)
│   ├── 02_academics/          # Calendars, exam circulars & regulations
│   ├── 03_campus_placements/  # Contacts, library, scholarships, placement data
│   ├── 04_accreditation/      # NAAC, NBA, NIRF, AICTE approvals
│   └── 05_student_faq/        # 40 authentic student Q&As (campus life, fests, hostels)
├── ingest.py                  # Chunking, metadata tagging & vector ingestion
├── main.py                    # FastAPI application & RAG query endpoint
├── requirements.txt           # Python dependencies
└── static/                    # Frontend chat widget UI
```

## Disclaimer
*This is an unofficial student project. Information is aggregated from public DSCE pages and peer student experiences. Please verify critical admission and fee details with the official DSCE admissions office.*
