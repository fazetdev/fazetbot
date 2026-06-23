import os
import faiss
import pickle
import numpy as np

from fastapi import FastAPI
from pydantic import BaseModel

from dotenv import load_dotenv

from google import genai
from sentence_transformers import SentenceTransformer


# Load environment variables
load_dotenv()

app = FastAPI()


# Request schema
class ChatRequest(BaseModel):
    message: str


# Gemini client (new SDK)
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# Load FAISS index
index = faiss.read_index("faiss_index.bin")


# Load chunks (with metadata)
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)


@app.get("/")
def home():
    return {"message": "Fazet AI API is running"}


@app.post("/chat")
def chat(request: ChatRequest):

    # 1. Get question
    question = request.message

    # 2. Embed question
    question_embedding = embedding_model.encode([question])
    question_embedding = np.array(question_embedding).astype("float32")

    # 3. FAISS search
    distances, indices = index.search(question_embedding, 5)

    # 4. Build context safely
    retrieved = [chunks[i] for i in indices[0]]

    context = "\n\n".join(
        item["text"] if isinstance(item, dict) else str(item)
        for item in retrieved
    )

    # 5. Extract sources safely
    sources = list(
        set(
            item["source"] for item in retrieved if isinstance(item, dict)
        )
    )

    # 6. Prompt
    prompt = f"""
You are an AI assistant for Fazet Edutech Ltd.

Answer ONLY using the information provided in the knowledge section.

If the answer is not present in the knowledge section, say:
"I could not find that information in the Fazet knowledge base."

Knowledge:
{context}

Question:
{question}
"""

    # 7. Gemini response
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # 8. Return API response
    return {
        "question": question,
        "answer": response.text,
        "sources": sources
    }