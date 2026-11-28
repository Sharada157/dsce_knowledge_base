"""
FastAPI Backend for DSCE RAG Chatbot
Provides conversational RAG with:
- Source link citations
- Multi-turn conversation memory
- Grounded "I don't know" fallback with verified campus contacts
- Contextual suggested follow-up questions
"""

import os
import re
from pathlib import Path

# Force HuggingFace to use local cached weights (prevents network hangs/timeouts)
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

# Load environment variables (.env)
load_dotenv()

# Configuration
CHROMA_DATA_PATH = Path("./chroma_db").resolve()
COLLECTION_NAME = "dsce_knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Initialize ChromaDB client & embedding function
chroma_client = None
collection = None

def get_or_refresh_collection():
    """Retrieve or re-initialize ChromaDB collection."""
    global chroma_client, collection
    if not CHROMA_DATA_PATH.exists():
        return None
    try:
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DATA_PATH))
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
        collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
        return collection
    except Exception as e:
        print(f"[WARNING] Could not load ChromaDB: {e}")
        return None

# Initial load on startup
get_or_refresh_collection()

# In-memory session memory: {session_id: [{"role": "user"|"assistant", "content": "..."}]}
session_store: Dict[str, List[Dict[str, str]]] = {}

# Out-of-Domain Detection & Guardrails
CAMPUS_KEYWORDS = {
    "dsce", "dayananda", "sagar", "college", "campus", "vtu", "comedk", "comed-k",
    "kcet", "cet", "pgcet", "gate", "admission", "admissions", "fee", "fees", "hostel",
    "hostels", "mess", "curfew", "outpass", "warden", "placement", "placements", "salary",
    "package", "packages", "attendance", "nsar", "iat", "cie", "see", "exam", "exams",
    "autonomous", "semester", "syllabus", "course", "courses", "engineering", "b.e",
    "be", "m.tech", "mba", "mca", "branch", "branches", "cse", "aiml", "ise", "ece",
    "eee", "mech", "civil", "biotech", "ai", "furore", "point blank", "club", "clubs",
    "library", "canteen", "shavige", "kumaraswamy", "layout", "bangalore", "bengaluru",
    "metro", "bmtc", "15-e", "15e", "kadirenahalli", "banashankari", "jp nagar",
    "dsu", "dsatm", "management quota", "quota", "cutoff", "cutoffs", "ranking", "nirf",
    "naac", "nba", "derbi", "cil", "scholarship", "scholarships", "principal", "hod",
    "building", "room", "counter", "challan", "eligibility", "documents", "verification"
}

OUT_OF_DOMAIN_PATTERNS = [
    r"\b(who is|who was)\s+(ronaldo|cristiano|messi|neymar|mbappe|dhoni|virat|kohli|sachin|rohit|modi|biden|trump|putin|obama|musk|elon|einstein|newton|shakespeare|gandhi|nehru)\b",
    r"\b(write|give|generate|create)\s+(a\s+|me\s+)?(python|java|c\+\+|c#|javascript|sql|html|css|code|script|program|function|algorithm)\b",
    r"\b(fibonacci|factorial|palindrome|bubble sort|quick sort|binary search|leetcode|hackerrank|codechef)\b",
    r"\b(weather in|temperature in|capital of|currency of|population of|president of|prime minister of)\b",
    r"\b(tell me a joke|write a poem|write a song|movie recommendation|recipe for|how to cook)\b",
    r"\b(what is the capital|who won the|fifa|world cup|ipl|champions league|ballon d'or)\b"
]

OUT_OF_DOMAIN_RESPONSE = (
    "I am specifically designed as the **Dayananda Sagar College of Engineering (DSCE) Campus Assistant**.\n\n"
    "I can only answer questions related to **DSCE** — including admissions, 2026–27 fee structures, "
    "VTU autonomous regulations, hostel facilities, campus transit, placements, and student clubs.\n\n"
    "I cannot assist with general trivia, programming generation tasks, or topics outside of DSCE. "
    "Please feel free to ask any question regarding DSCE!"
)

# Contact fallbacks for "I don't know" or out-of-scope queries
FALLBACK_CONTACTS = """
I could not find definitive official information about that in the current public college knowledge base. 
To get accurate guidance, please contact the respective college office:

- **Admissions Office:** +91-80-42161750 / 51, +91 9916075170 | `admissions@dayanandasagar.edu`
- **Fee Section (Building 1, Room 206):** +91-80-26662226 (Ext 120) | `feesection-dsce@dayanandasagar.edu`
- **Controller of Examinations (COE):** +91-80-42161770 | `coe-dsce@dayanandasagar.edu`
- **Indian Boys Hostel:** 080-42161701 | **Girls Hostel:** 080-42161727 / 080-42162727
- **Central Placement Cell:** +91-80-26663981 | `placement@dayanandasagar.edu`
- **Main Reception:** 080-42161708 (Ext 708)
"""

SYSTEM_PROMPT_TEMPLATE = """You are the official student-built AI assistant for Dayananda Sagar College of Engineering (DSCE), Bengaluru.
Your goal is to answer queries with exceptional clarity, high precision, and professional formatting based strictly on the provided context.

CRITICAL SCOPE BOUNDARY & OUT-OF-DOMAIN RESTRICTION:
- You are exclusively an information assistant for Dayananda Sagar College of Engineering (DSCE).
- You MUST NEVER answer general knowledge questions, world trivia (e.g., celebrities, sports stars like Ronaldo or Messi, movies, geography), general coding requests (e.g., write Python code, Fibonacci series, sorting algorithms), or non-DSCE queries.
- Answer ONLY topics directly related to DSCE: admissions, fees, hostel rules, academics, autonomous VTU exams, placements, campus facilities, and student life.
- If a question is not about DSCE, you MUST refuse immediately and concisely:
  "I am specifically designed as the DSCE Campus Assistant to answer questions about Dayananda Sagar College of Engineering (admissions, fees, campus facilities, academics, hostels, and placements). I cannot assist with general trivia, programming requests, or non-college topics. Please ask a question related to DSCE!"
- NEVER use your general pre-trained training knowledge to answer out-of-domain queries.

OUTPUT & FORMATTING GUIDELINES:
1. Direct, Crisp Summary Upfront:
   - Begin with a direct, clear 1-2 sentence answer addressing the user's question immediately.
   - Do NOT use generic greetings like "Hello! As an AI..." or repetitious introductions.
2. Structured & Clean Arrangement:
   - Organize information using clean subheadings (`### Section Name`) or bold bullet points (`* **Feature/Item:** Description`).
   - For fee structures, hostel schedules, placement stats, cutoffs, or institution comparisons (DSCE vs DSU vs DSATM), ALWAYS use clean Markdown tables.
   - For multi-step procedures (admissions, fee payment, outpass, backlog registration), use clear numbered steps (1., 2., 3.).
3. Conciseness & No Cluttered Inline Citations:
   - Keep answers short, punchy, and detailed without unnecessary filler.
   - Do NOT include messy inline URLs or citations in the body text (the web interface automatically provides an expandable citations list below your response).
4. Conversational Continuity & Contextual Memory:
   - Carefully review the CONVERSATION HISTORY before answering.
   - If the user's latest question references prior turns or uses pronouns (such as "it", "that", "this fee", "the hostel mentioned", "there", "them", "how to pay", "and for the other one?"), explicitly resolve the reference and seamlessly connect your answer to the previous discussion.
   - Acknowledge earlier context naturally (e.g., "Connecting to the COMED-K fee of ₹3,22,000 we discussed...", or "Regarding the Indian Boys Hostel mentioned earlier...").
5. Accurate Grounding & Fallback:
   - Rely strictly on the facts in the CONTEXT below. Never invent fees, numbers, or policies.
   - If information is not found in the context, succinctly state that official records are not in the current public documents and provide the relevant official campus contact (phone/email/office room).

CONTEXT:
{context}

CONVERSATION HISTORY:
{history}

USER QUESTION: {query}
"""

app = FastAPI(
    title="DSCE Knowledge Assistant API",
    description="RAG backend for Dayananda Sagar College of Engineering",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's query")
    session_id: Optional[str] = Field("default_session", description="Session identifier for multi-turn history")
    top_k: Optional[int] = Field(4, description="Number of context chunks to retrieve")


class SourceItem(BaseModel):
    title: str
    source_url: str
    category: str
    section: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
    suggested_questions: List[str]
    session_id: str


def call_llm(prompt: str) -> Optional[str]:
    """Invoke Groq API (Primary), Gemini API (Secondary), Ollama (Local), or return None for fallback."""
    
    # 1. Try Groq API (Ultra-fast inference on LPUs)
    groq_api_key = os.getenv("GROQ_API_KEY", "")
    if groq_api_key:
        try:
            from groq import Groq
            groq_client = Groq(api_key=groq_api_key, timeout=15.0)
            groq_models = [
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "qwen/qwen3.8-27b"
            ]
            for model_name in groq_models:
                try:
                    chat_resp = groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model=model_name,
                        temperature=0.2,
                        max_tokens=1000
                    )
                    content = chat_resp.choices[0].message.content
                    if content and content.strip():
                        return content.strip()
                except Exception as g_err:
                    print(f"[Groq Notice: {model_name} error: {g_err}. Trying next...]")
                    continue
        except Exception as e:
            print(f"[Groq Client Notice] {e}")

    # 2. Try Gemini API
    api_key = os.getenv("GEMINI_API_KEY", "")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=25000)
            )
            # Reliable active models ordered by current available quota
            candidate_models = [
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash",
                "gemini-3.6-flash"
            ]
            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    print(f"[Gemini Notice: {model_name} error: {model_err}. Trying next...]")
                    continue
        except Exception as e:
            print(f"[Gemini API Client Notice] {e}")

    # 3. Try Ollama if running locally
    try:
        import requests
        res = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=10
        )
        if res.status_code == 200:
            return res.json().get("response", "")
    except Exception:
        pass

    # 4. Fallback to clean RAG extractive synthesis
    return None


def generate_suggested_questions(query: str, answer: str) -> List[str]:
    """Generate 3 contextual follow-up questions based on topic."""
    q_lower = query.lower()
    
    if any(k in q_lower for k in ["fee", "fees", "comedk", "cet", "kea", "management"]):
        return [
            "What documents are required during reporting at DSCE?",
            "What is the hostel fee structure for 1st year?",
            "How do I pay the fees online or at the Fee Section?"
        ]
    elif any(k in q_lower for k in ["hostel", "mess", "food", "room", "curfew"]):
        return [
            "What are the curfew timings for boys and girls hostels?",
            "Are there good PGs available near Kumaraswamy Layout?",
            "What is the procedure for an overnight hostel outpass?"
        ]
    elif any(k in q_lower for k in ["placement", "package", "salary", "recruit", "companies"]):
        return [
            "What is the minimum CGPA required for placement eligibility?",
            "Tell me about the Point Blank coding club",
            "What role does CIL play in placement training?"
        ]
    elif any(k in q_lower for k in ["exam", "attendance", "iat", "nsar", "calendar"]):
        return [
            "What happens if my attendance falls below 75%?",
            "How are CIE and SEE marks calculated?",
            "When are the semester end exams for odd semesters?"
        ]
    elif any(k in q_lower for k in ["bus", "metro", "reach", "route", "commute", "travel", "address", "location", "stop", "station"]):
        return [
            "What is the nearest Green Line metro station to DSCE?",
            "Which BMTC bus goes directly to Dayananda Sagar gate?",
            "What is the difference between DSCE, DSU, and DSATM?"
        ]
    elif any(k in q_lower for k in ["dsu", "dsatm", "institution", "difference", "campus"]):
        return [
            "What is the difference between DSCE, DSU, and DSATM?",
            "What is the exact postal address of DSCE campus?",
            "Are placements combined across DSCE, DSU, and DSATM?"
        ]
    else:
        return [
            "What is the exact address of DSCE and nearest metro station?",
            "What is the difference between DSCE, DSU, and DSATM?",
            "What are the B.E. COMEDK fee details for 2026-27?"
        ]


@app.get("/api/health")
def health_check():
    """Health check verifying vector database and status."""
    total_docs = collection.count() if collection else 0
    has_groq = bool(os.getenv("GROQ_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "online",
        "vector_db_loaded": collection is not None,
        "indexed_chunks": total_docs,
        "embedding_model": EMBEDDING_MODEL,
        "llm_configured": has_groq or has_gemini,
        "primary_provider": "groq (LPUs)" if has_groq else ("gemini" if has_gemini else "fallback")
    }


@app.get("/api/test-questions")
def get_test_questions():
    """Returns sample benchmark queries for UI testing."""
    return [
        {"category": "Campus & Commute", "question": "What is the official address of DSCE, nearest metro stations, and direct bus routes?"},
        {"category": "Campus & Commute", "question": "What is the difference between DSCE, DSU, and DSATM?"},
        {"category": "Admissions & Fees", "question": "What is the 1st year B.E. COMEDK fee for Karnataka students in 2026-27?"},
        {"category": "Admissions & Fees", "question": "What is the management quota tuition fee for CSE and AIML?"},
        {"category": "Hostel & Living", "question": "What are the curfew timings for boys and girls hostels?"},
        {"category": "Hostel & Living", "question": "How is the mess food and what meals are provided daily?"},
        {"category": "Academics", "question": "What is the attendance rule and what happens if I get NSAR?"},
        {"category": "Academics", "question": "How are CIE and SEE marks split for grading?"},
        {"category": "Placements", "question": "What are the average and highest packages for Computer Science?"},
        {"category": "Campus Life", "question": "What is Point Blank and how can I join the club?"},
        {"category": "Campus Life", "question": "Tell me about the annual cultural fest FURORE."}
    ]


def contextualize_retrieval_query(query: str, history: List[Dict[str, str]]) -> str:
    """Enhances retrieval query with recent conversation context if the query has anaphoric references or is a follow-up."""
    if not history:
        return query
    
    referential_keywords = {
        "it", "that", "this", "they", "them", "there", "same", "pay", "payment",
        "where", "when", "curfew", "mess", "fees", "fee", "concession", "refund",
        "counter", "room", "hostel", "rules", "eligibility", "documents", "second",
        "first", "both", "differ", "difference", "what about", "is there", "and",
        "how", "why", "apply", "who", "which", "cost", "dates", "schedule"
    }
    
    words = set(re.findall(r"\w+", query.lower()))
    is_short = len(words) <= 5
    has_ref = bool(words & referential_keywords)
    
    if is_short or has_ref:
        # Retrieve recent user queries from history to supply topic context
        recent_user_turns = [m["content"] for m in history if m["role"] == "user"][-2:]
        if recent_user_turns:
            return f"{' '.join(recent_user_turns)} {query}"
            
    return query


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """Processes user query through the RAG pipeline with multi-turn memory and strict domain guardrails."""
    query = req.query.strip()
    session_id = req.session_id or "default_session"
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query_lower = query.lower()

    # 1. Regex check for obvious out-of-domain queries (celebrities, coding requests, general trivia)
    if any(re.search(pat, query_lower) for pat in OUT_OF_DOMAIN_PATTERNS):
        return ChatResponse(
            answer=OUT_OF_DOMAIN_RESPONSE,
            sources=[],
            suggested_questions=[
                "What is the 1st year B.E. COMEDK fee for 2026-27?",
                "What is the difference between DSCE, DSU, and DSATM?",
                "What are the hostel curfew timings and mess rules?"
            ],
            session_id=session_id
        )

    # Format multi-turn conversation history (keeping last 6 messages / 3 full turns)
    history = session_store.get(session_id, [])
    history_str = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history[-6:]])

    # Contextualize retrieval query using conversation history for follow-up references
    retrieval_query = contextualize_retrieval_query(query, history)

    # 2. Retrieve top-k context chunks from ChromaDB (with auto-reconnect on index refresh)
    global collection
    col = collection or get_or_refresh_collection()
    if col is None:
        raise HTTPException(status_code=503, detail="Vector index not found. Please run ingest.py first.")

    try:
        results = col.query(
            query_texts=[retrieval_query],
            n_results=req.top_k or 4
        )
    except Exception as query_err:
        print(f"[Notice: Refreshing collection after {query_err}]")
        col = get_or_refresh_collection()
        if col is None:
            raise HTTPException(status_code=503, detail="Vector index not found.")
        results = col.query(
            query_texts=[retrieval_query],
            n_results=req.top_k or 4
        )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0] if "distances" in results else []
    min_dist = min(distances) if distances else 1.0

    # 3. Vector distance threshold: check if query is completely unrelated to college documents
    has_campus_term = any(k in query_lower for k in CAMPUS_KEYWORDS)
    if min_dist >= 0.76 and not has_campus_term:
        return ChatResponse(
            answer=OUT_OF_DOMAIN_RESPONSE,
            sources=[],
            suggested_questions=[
                "What is the 1st year B.E. COMEDK fee for 2026-27?",
                "What is the difference between DSCE, DSU, and DSATM?",
                "What are the hostel curfew timings and mess rules?"
            ],
            session_id=session_id
        )

    # Format context and sources
    context_parts = []
    sources: List[SourceItem] = []
    seen_urls = set()

    for doc, meta in zip(documents, metadatas):
        context_parts.append(doc)
        url = meta.get("source_url", "")
        title = meta.get("title", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            sources.append(SourceItem(
                title=title,
                source_url=url,
                category=meta.get("category", "general"),
                section=meta.get("section", "")
            ))

    context_str = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant documents found."

    # Format multi-turn conversation history for prompt (last 6 messages / 3 Q&A pairs)
    history_str = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in history[-6:]])

    # 2. Build Prompt
    full_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        context=context_str,
        history=history_str if history_str else "None",
        query=query
    )

    # 3. Generate Answer
    answer = call_llm(full_prompt)

    # Fallback response if LLM API is temporarily busy
    if not answer:
        if documents:
            clean_paragraphs = []
            for doc in documents[:3]:
                # Clean section tags, headers, and Q&A labels
                cleaned = re.sub(r"^\[.*?\]\s*\n", "", doc).strip()
                cleaned = re.sub(r"^(?:#{1,6}\s*)?Q\d+:\s*.*?\n(?:\*{1,2})?[Aa](?:\*{1,2})?:\s*", "", cleaned).strip()
                if cleaned and cleaned not in clean_paragraphs:
                    clean_paragraphs.append(cleaned)
            combined = "\n\n".join(clean_paragraphs)
            answer = f"Based on verified Dayananda Sagar College of Engineering (DSCE) records:\n\n{combined}\n\n*If you need further assistance or room allotment details, please contact the relevant campus office:* \n- **Admissions / General Enquiries:** 080-42161750 / 51\n- **Girls Hostel Office:** 080-42161727\n- **Boys Hostel Office:** 080-42161701"
        else:
            answer = FALLBACK_CONTACTS

    # 4. Update session history
    if session_id not in session_store:
        session_store[session_id] = []
    session_store[session_id].append({"role": "user", "content": query})
    session_store[session_id].append({"role": "assistant", "content": answer})

    # Clean sources if refusal was returned by LLM
    ans_lower = answer.lower()
    if "outside of dsce" in ans_lower or "cannot assist with general" in ans_lower or ("dsce campus assistant" in ans_lower and "cannot assist" in ans_lower):
        sources = []

    # Generate follow-up suggestions
    suggested = generate_suggested_questions(query, answer)

    return ChatResponse(
        answer=answer,
        sources=sources,
        suggested_questions=suggested,
        session_id=session_id
    )


# Mount static frontend files
static_dir = Path("./static").resolve()
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def serve_index(embed: Optional[str] = None):
    """Serves the realistic official DSCE website or embedded widget."""
    if embed == "true":
        chat_path = static_dir / "chat.html"
        if chat_path.exists():
            return FileResponse(chat_path)
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "DSCE RAG Chatbot API is running. Access /docs for Swagger API."}


@app.get("/chat")
def serve_chat():
    """Serves the full-screen interactive RAG assistant workbench."""
    chat_path = static_dir / "chat.html"
    if chat_path.exists():
        return FileResponse(chat_path)
    return FileResponse(static_dir / "index.html")
