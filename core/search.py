from sentence_transformers import SentenceTransformer
from utils.chunk_loader import chunk_text
from utils.pdf_loader import load_pdf
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")


pdf_text = load_pdf("documents/fazet_corporate_profile.pdf")


chunks = chunk_text(pdf_text, chunk_size=500)


chunk_embeddings = model.encode(chunks)


question = input("Ask a question: ")


question_embedding = model.encode(question)


scores = np.dot(chunk_embeddings, question_embedding)


top_indices = np.argsort(scores)[-3:][::-1]


print("\nTop Matches:\n")


for i in top_indices:
    print("=" * 50)
    print(chunks[i])