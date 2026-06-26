import os
import psycopg2
from dotenv import load_dotenv
import google.generativeai as genai

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# =========================
# INIT & VALIDATION
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

API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in environment")
if not DATABASE_URL:
    raise ValueError("Missing DATABASE_URL in environment")

# Configure Gemini
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/text-embedding-004" # 768-dimensional cloud embedding
TOP_K = 5

print("System Ready")

# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    message: str

# =========================
# RETRIEVAL (Neon Serverless Postgres)
# =========================
def retrieve_context(question: str):
    try:
        # 1. Generate embedding using Gemini Cloud API
        embedding_response = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=question,
            task_type="retrieval_query"
        )
        query_vector = embedding_response['embedding']

        # 2. Query Neon Database using pgvector cosine distance (<=>)
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Pulling content from your new markdown chunks table
        cursor.execute(f"""
            SELECT content FROM fazetbot_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
        """, (query_vector, TOP_K))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [row[0] for row in rows]
    except Exception as e:
        print(f"Database/Embedding retrieval error: {str(e)}")
        return []

# =========================
# PROMPT BUILDER
# =========================
def build_prompt(question: str, context: str):
    return f"""
You are Fazet AI Assistant.

Use ONLY the knowledge base below to answer the user's question. 

If the answer is not found or cannot be fully justified based on the provided text context, state clearly:
"I don't know based on the available knowledge base."

Knowledge Base:
{context}

Question:
{question}
"""

# =========================
# API ROUTE
# =========================
@app.post("/api/chat") # Prefixed with /api/ to align with vercel.json routing
def chat(req: ChatRequest):
    question = req.message

    context_chunks = retrieve_context(question)
    context = "\n\n".join(context_chunks)

    prompt = build_prompt(question, context)

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"Error generating response from Gemini: {str(e)}"

    return {
        "question": question,
        "answer": answer,
        "sources": context_chunks
    }

# =========================
# FRONTEND STATIC ROUTING
# =========================
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")