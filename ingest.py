"""
DSCE Knowledge Base Ingestion Pipeline
Chunks Markdown files preserving front-matter metadata, tables, and FAQ pairs,
then embeds and indexes into a persistent local ChromaDB collection using all-MiniLM-L6-v2.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.utils import embedding_functions

CHROMA_DATA_PATH = Path("./chroma_db").resolve()
COLLECTION_NAME = "dsce_knowledge_base"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
DOCS_DIR = Path("./dsce_knowledge_base").resolve()


def parse_frontmatter(content: str) -> tuple[Dict[str, str], str]:
    """Extract YAML front-matter and remaining markdown body."""
    meta = {}
    body = content
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        raw_meta, body = match.group(1), match.group(2)
        for line in raw_meta.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                meta[key] = val
    return meta, body


def chunk_faq_file(body: str, base_meta: Dict[str, str], file_rel: str) -> List[Dict[str, Any]]:
    """Split student FAQ file into distinct Q&A chunks for optimal retrieval."""
    chunks = []
    # Split by ### Q<number>: or ## Section
    qa_blocks = re.split(r"(?=(?:^###\s+Q\d+:))", body, flags=re.MULTILINE)
    
    current_category = "student_faq"
    for block in qa_blocks:
        block = block.strip()
        if not block:
            continue
        
        # Check if it's a section header before Q1
        if block.startswith("## ") and not block.startswith("### Q"):
            lines = block.splitlines()
            current_category = lines[0].replace("##", "").strip()
            continue
            
        # Extract question line
        first_line = block.splitlines()[0]
        q_match = re.search(r"###\s+(Q\d+:\s*.*?)$", first_line)
        question_title = q_match.group(1) if q_match else "FAQ"
        
        chunk_text = f"[{base_meta.get('title', 'DSCE FAQ')} > {question_title}]\n{block}"
        chunk_meta = {
            "source_url": base_meta.get("source_url", "student-contributed"),
            "title": base_meta.get("title", "Student FAQ"),
            "category": base_meta.get("category", "student_life"),
            "file": file_rel,
            "section": question_title,
        }
        chunks.append({"text": chunk_text, "meta": chunk_meta})
    return chunks


def chunk_markdown_file(body: str, base_meta: Dict[str, str], file_rel: str) -> List[Dict[str, Any]]:
    """Split general markdown files by H2/H3 headers, keeping tables intact."""
    chunks = []
    # Split by H2 headers (## )
    sections = re.split(r"(?=(?:^##\s+))", body, flags=re.MULTILINE)
    doc_title = base_meta.get("title", file_rel)

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        
        # Determine section title
        first_line = sec.splitlines()[0] if sec.splitlines() else ""
        if first_line.startswith("## "):
            sec_title = first_line.replace("##", "").strip()
        elif first_line.startswith("# "):
            sec_title = first_line.replace("#", "").strip()
        else:
            sec_title = "Overview"

        # If section is small enough (under 1800 chars), keep as single chunk (preserves tables)
        if len(sec) <= 1800:
            chunk_text = f"[{doc_title} > {sec_title}]\n{sec}"
            chunks.append({
                "text": chunk_text,
                "meta": {
                    "source_url": base_meta.get("source_url", ""),
                    "title": doc_title,
                    "category": base_meta.get("category", "general"),
                    "file": file_rel,
                    "section": sec_title,
                }
            })
        else:
            # Further split by H3 if present, or paragraphs
            sub_sections = re.split(r"(?=(?:^###\s+))", sec, flags=re.MULTILINE)
            if len(sub_sections) > 1:
                for sub in sub_sections:
                    sub = sub.strip()
                    if not sub:
                        continue
                    sub_first = sub.splitlines()[0]
                    sub_title = sub_first.replace("###", "").strip() if sub_first.startswith("### ") else sec_title
                    chunk_text = f"[{doc_title} > {sec_title} > {sub_title}]\n{sub}"
                    chunks.append({
                        "text": chunk_text,
                        "meta": {
                            "source_url": base_meta.get("source_url", ""),
                            "title": doc_title,
                            "category": base_meta.get("category", "general"),
                            "file": file_rel,
                            "section": f"{sec_title} - {sub_title}",
                        }
                    })
            else:
                # Split by double newline paragraphs
                paragraphs = sec.split("\n\n")
                current_chunk = []
                current_len = 0
                for p in paragraphs:
                    p = p.strip()
                    if not p:
                        continue
                    if current_len + len(p) > 1200 and current_chunk:
                        chunk_text = f"[{doc_title} > {sec_title}]\n" + "\n\n".join(current_chunk)
                        chunks.append({
                            "text": chunk_text,
                            "meta": {
                                "source_url": base_meta.get("source_url", ""),
                                "title": doc_title,
                                "category": base_meta.get("category", "general"),
                                "file": file_rel,
                                "section": sec_title,
                            }
                        })
                        current_chunk = [p]
                        current_len = len(p)
                    else:
                        current_chunk.append(p)
                        current_len += len(p)
                if current_chunk:
                    chunk_text = f"[{doc_title} > {sec_title}]\n" + "\n\n".join(current_chunk)
                    chunks.append({
                        "text": chunk_text,
                        "meta": {
                            "source_url": base_meta.get("source_url", ""),
                            "title": doc_title,
                            "category": base_meta.get("category", "general"),
                            "file": file_rel,
                            "section": sec_title,
                        }
                    })
    return chunks


def build_knowledge_chunks(docs_dir: Path) -> List[Dict[str, Any]]:
    """Scan docs directory and generate all chunks with metadata."""
    all_chunks = []
    # Find all .md files excluding top-level README
    for file_path in sorted(docs_dir.rglob("*.md")):
        if file_path.name == "README.md" and file_path.parent == docs_dir:
            continue
        
        rel_path = file_path.relative_to(docs_dir).as_posix()
        content = file_path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        
        if "student-faq" in rel_path or "faq" in rel_path:
            file_chunks = chunk_faq_file(body, meta, rel_path)
        else:
            file_chunks = chunk_markdown_file(body, meta, rel_path)
            
        all_chunks.extend(file_chunks)
    return all_chunks


def ingest_to_chroma():
    """Build and persist vector embeddings into ChromaDB."""
    print("=" * 60)
    print("Starting DSCE Knowledge Ingestion Pipeline")
    print(f"Reading documents from: {DOCS_DIR}")
    print(f"ChromaDB persistence path: {CHROMA_DATA_PATH}")
    print("=" * 60)

    chunks = build_knowledge_chunks(DOCS_DIR)
    print(f"-> Generated {len(chunks)} contextual chunks across knowledge base.")

    # Setup Chroma client with local persistence
    client = chromadb.PersistentClient(path=str(CHROMA_DATA_PATH))
    
    # Use sentence-transformers all-MiniLM-L6-v2
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    # Recreate collection to prevent stale or duplicate entries
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print(f"-> Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
        metadata={"description": "DSCE Admissions, Academics, Placements & Student Knowledge Base"}
    )

    # Prepare batch arrays
    ids = [f"chunk_{i:04d}" for i in range(len(chunks))]
    documents = [c["text"] for c in chunks]
    metadatas = [c["meta"] for c in chunks]

    # Ingest in batches of 64
    batch_size = 64
    for i in range(0, len(chunks), batch_size):
        end = min(i + batch_size, len(chunks))
        collection.add(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end],
        )
        print(f"   Indexed chunks {i+1} to {end}...")

    total_indexed = collection.count()
    print(f"\n[SUCCESS] Successfully indexed {total_indexed} chunks into ChromaDB collection '{COLLECTION_NAME}'.")

    # Run verification queries
    print("\n--- Running Sanity Retrieval Tests ---")
    test_queries = [
        "What are the hostel curfew and gate timings?",
        "What is the COMEDK fee structure for Karnataka students?",
        "What is the minimum attendance requirement and NSAR rule?",
        "Tell me about the Point Blank coding club"
    ]

    for q in test_queries:
        print(f"\n[Test Query]: '{q}'")
        res = collection.query(query_texts=[q], n_results=1)
        top_doc = res["documents"][0][0] if res["documents"] else "None"
        top_meta = res["metadatas"][0][0] if res["metadatas"] else {}
        first_line = top_doc.splitlines()[0] if top_doc else ""
        print(f"  -> Top Match: {first_line}")
        print(f"  -> Source: {top_meta.get('title')} ({top_meta.get('source_url')})")

    print("\n[DONE] Ingestion and retrieval verification completed successfully.")


if __name__ == "__main__":
    ingest_to_chroma()
