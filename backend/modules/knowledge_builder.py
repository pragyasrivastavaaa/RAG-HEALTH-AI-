"""
RAG Knowledge Base Builder
===========================
Reads all .txt files from the knowledge_base/ folder,
splits them into overlapping chunks, embeds each chunk
using a free local sentence-transformers model, and stores
the result as a FAISS index.

Run ONCE from rag-health-ai/ root before using the app:
    python backend/modules/knowledge_builder.py

After running you will see:
    vector_store/index.faiss
    vector_store/index.pkl

These are loaded at query time by rag_engine.py.
"""

import os
import pickle
import sys

# Allow running as a script from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import Config

# ── Constants ─────────────────────────────────────────────────────────────
CHUNK_SIZE    = 400    # characters per chunk
CHUNK_OVERLAP = 80     # overlap between chunks (maintains context)


def load_documents(knowledge_dir: str) -> list[dict]:
    """
    Load all .txt files from knowledge_base/ directory.
    Returns list of { text, source } dicts.
    """
    documents = []
    for fname in os.listdir(knowledge_dir):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(knowledge_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        documents.append({"text": content, "source": fname})
        print(f"  Loaded: {fname} ({len(content)} chars)")
    return documents


def split_into_chunks(documents: list[dict]) -> list[dict]:
    """
    Split each document into overlapping chunks.
    Overlapping ensures context is not lost at chunk boundaries.
    """
    chunks = []
    for doc in documents:
        text   = doc["text"]
        source = doc["source"]
        start  = 0
        while start < len(text):
            end   = min(start + CHUNK_SIZE, len(text))
            chunk = text[start:end].strip()
            if len(chunk) > 50:    # skip tiny chunks
                chunks.append({"text": chunk, "source": source})
            start += CHUNK_SIZE - CHUNK_OVERLAP
    print(f"\n  Total chunks created: {len(chunks)}")
    return chunks


def build_faiss_index(chunks: list[dict], vector_store_dir: str):
    """
    Embed chunks using free local sentence-transformers model,
    then build and save FAISS index.

    Model used: all-MiniLM-L6-v2
    - Free, runs 100% locally (no API key needed)
    - 384-dimensional embeddings
    - Fast and accurate for semantic search
    """
    try:
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
    except ImportError as e:
        print(f"ERROR: Missing package — {e}")
        print("Run: pip install sentence-transformers faiss-cpu")
        return False

    print("\n  Loading embedding model (all-MiniLM-L6-v2)...")
    print("  This downloads ~90MB on first run, then cached locally.")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [c["text"] for c in chunks]

    print(f"  Embedding {len(texts)} chunks...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32,
        convert_to_numpy=True
    )

    # Build FAISS index (L2 distance = cosine similarity for normalised vectors)
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings.astype("float32"))

    # Save index + metadata
    os.makedirs(vector_store_dir, exist_ok=True)
    faiss.write_index(index, os.path.join(vector_store_dir, "index.faiss"))
    with open(os.path.join(vector_store_dir, "index.pkl"), "wb") as f:
        pickle.dump({"chunks": chunks, "model": "all-MiniLM-L6-v2"}, f)

    print(f"\n  FAISS index saved → {vector_store_dir}/index.faiss")
    print(f"  Metadata saved   → {vector_store_dir}/index.pkl")
    print(f"  Index contains {index.ntotal} vectors of dimension {dim}")
    return True


def main():
    print("=" * 55)
    print("  RAG Health AI — Knowledge Base Builder")
    print("=" * 55)

    # Walk up from backend/modules/ → backend/ → project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    kb_dir = os.path.join(project_root, "knowledge_base")
    vs_dir = os.path.join(project_root, "vector_store")

    if not os.path.exists(kb_dir):
        print(f"ERROR: knowledge_base/ folder not found at {kb_dir}")
        return

    txt_files = [f for f in os.listdir(kb_dir) if f.endswith(".txt")]
    if not txt_files:
        print("ERROR: No .txt files found in knowledge_base/")
        return

    print(f"\nLoading documents from: {kb_dir}")
    docs   = load_documents(kb_dir)
    chunks = split_into_chunks(docs)

    print("\nBuilding FAISS vector index...")
    success = build_faiss_index(chunks, vs_dir)

    if success:
        print("\n" + "=" * 55)
        print("  Knowledge base built successfully!")
        print("  You can now run the app: cd backend && flask run")
        print("=" * 55)
    else:
        print("\nKnowledge base build FAILED. Check errors above.")


if __name__ == "__main__":
    main()