"""Utility functions for RAG using Weaviate + Ollama/OpenAI-compatible LLM."""

import os
from typing import List

import weaviate
import openai

# Configure from env vars or defaults
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")  # or "kimi", etc.
# Configure OpenAI-compatible client (Ollama)
openai.api_key = "ollama"  # any string when hitting local Ollama server
openai.api_base = f"{OLLAMA_BASE_URL}/v1"

_client: weaviate.Client | None = None

def get_weaviate_client() -> weaviate.Client:
    global _client
    if _client is None:
        _client = weaviate.Client(url=WEAVIATE_URL)
    return _client


def semantic_search(question: str, top_k: int = 5) -> List[str]:
    """Perform a vector search in Weaviate and return text chunks."""
    client = get_weaviate_client()
    result = (
        client.query
        .get("Document", ["text"])
        .with_near_text({"concepts": [question]})
        .with_limit(top_k)
        .do()
    )
    texts: List[str] = [d["text"] for d in result["data"]["Get"]["Document"]]
    return texts


def generate_answer(question: str, context_chunks: List[str]) -> str:
    """Call Ollama (OpenAI-compatible) to generate answer."""
    context = "\n".join(context_chunks)
    prompt = (
        "Answer the question using the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\nAnswer:"
    )
    response = openai.ChatCompletion.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def rag_query(question: str) -> dict:
    """End-to-end RAG pipeline."""
    chunks = semantic_search(question)
    answer = generate_answer(question, chunks)
    return {"answer": answer, "sources": chunks}
