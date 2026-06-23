from sentence_transformers import SentenceTransformer
import numpy as np

from utils.chunk_loader import chunk_text
from utils.pdf_loader import load_pdf


model = SentenceTransformer("all-MiniLM-L6-v2")

pdf_text = load_pdf("documents/fazet_corporate_profile.pdf")

chunks = chunk_text(pdf_text, chunk_size=500)

embeddings = model.encode(chunks)

print("Total chunks:", len(chunks))
print("Total embeddings:", len(embeddings))
print("Embedding size:", len(embeddings[0]))