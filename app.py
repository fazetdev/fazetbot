import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# 1. Initialize Clients
API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

if not API_KEY or not DATABASE_URL:
    raise ValueError("Missing essential environment configuration variables.")

client = genai.Client(api_key=API_KEY)
app = FastAPI()

# Enable CORS so your frontend on port 5500 can talk to port 5000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, perfect for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Generate query embedding
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=request.message,
            config=types.EmbedContentConfig(output_dimensionality=768)
        )
        query_vector = response.embeddings[0].values

        # Query Neon Database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT content FROM fazetbot_chunks 
            ORDER BY embedding <=> %s::vector 
            LIMIT 3;
        """, (query_vector,))
        
        results = cursor.fetchall()
        context = "\n".join([row[0] for row in results])
        
        cursor.close()
        conn.close()

        # Generate response using Gemini
        ai_response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Context:\n{context}\n\nUser Question: {request.message}"
        )
        
        return {"response": ai_response.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FazetBot FastAPI Backend Core with CORS...")
    uvicorn.run(app, host="127.0.0.1", port=5000)
