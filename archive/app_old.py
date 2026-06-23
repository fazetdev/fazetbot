import os
import faiss
import pickle
import numpy as np

from dotenv import load_dotenv

import google.generativeai as genai
from sentence_transformers import SentenceTransformer

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

llm = genai.GenerativeModel("gemini-2.5-flash")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
index = faiss.read_index("faiss_index.bin")

# Load metadata
with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

question = input("Ask a question: ")

question_embedding = embedding_model.encode([question])
question_embedding = np.array(question_embedding).astype("float32")

distances, indices = index.search(question_embedding, 10)

retrieved_chunks = [chunks[i] for i in indices[0]]

context = "\n\n".join(
    [item["text"] for item in retrieved_chunks]
)

sources = sorted(
    set(item["source"] for item in retrieved_chunks)
)

prompt = f"""
You are an AI assistant for Fazet Edutech Ltd.

Answer ONLY using the provided knowledge.

If the answer is not present in the knowledge base, say:
"I could not find that information in the knowledge base."

Knowledge:
{context}

Question:
{question}
"""

response = llm.generate_content(prompt)

print("\nAnswer:\n")
print(response.text)

print("\nSources:\n")

for source in sources:
    print("-", source)