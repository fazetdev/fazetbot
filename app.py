import os
import pickle

import faiss
from dotenv import load_dotenv
from google import genai
from sentence_transformers import SentenceTransformer

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =========================
# INIT
# =========================

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CONFIG
# =========================

MODEL_NAME = "gemini-2.5-flash"
TOP_K = 6
MAX_DISTANCE = 1.5

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

FAISS_INDEX_FILE = "faiss_index.bin"
CHUNKS_FILE = "chunks.pkl"

# =========================
# VALIDATION
# =========================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment")

# =========================
# LOAD MODELS
# =========================

client = genai.Client(api_key=API_KEY)

index = faiss.read_index(FAISS_INDEX_FILE)

with open(CHUNKS_FILE, "rb") as f:
    chunks = pickle.load(f)

print("System Ready")

# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):
    message: str

# =========================
# RETRIEVAL
# =========================

def retrieve_context(question: str):
    embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    distances, indices = index.search(embedding, TOP_K)

    results = []

    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue

        if dist > MAX_DISTANCE:
            continue

        results.append(chunks[idx]["text"])

    return results

# =========================
# PROMPT
# =========================

def build_prompt(question: str, context: str):
    return f"""
You are Fazet AI Assistant.

Use ONLY the knowledge base below.

If answer is not found, say:
"I don't know based on the available knowledge base."

Knowledge Base:
{context}

Question:
{question}
"""

# =========================
# GEMINI
# =========================

def generate_answer(prompt: str):
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# =========================
# API ROUTE
# =========================

@app.post("/chat")
def chat(req: ChatRequest):

    question = req.message

    context_chunks = retrieve_context(question)
    context = "\n\n".join(context_chunks)

    prompt = build_prompt(question, context)

    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": context_chunks
    }

# =========================
# HEALTH CHECK
# =========================

@app.get("/")
def home():
    return {"message": "Fazet AI API is running"}