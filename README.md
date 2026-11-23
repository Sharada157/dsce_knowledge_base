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
[LLM (Gemini / Ollama)] <── [Retrieved Chunks + Source URLs]
     │
     ▼
[Response with Verified Citations + Suggested Questions]
```

## Tech Stack
- **Vector Database:** ChromaDB (local persistence, zero setup)
- **Embeddings:** `all-MiniLM-L6-v2` via `sentence-transformers`
- **LLM:** Google Gemini API (`google-genai`) / Ollama API
- **Backend:** FastAPI (Python)
- **Frontend:** Lightweight Vanilla HTML/CSS/JavaScript floating widget
- **Data Sources:** Official DSCE public documents & student-contributed campus FAQ

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
