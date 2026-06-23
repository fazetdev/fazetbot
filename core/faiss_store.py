import os
import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer

from utils.pdf_loader import load_pdf
from utils.chunk_loader import chunk_text


model = SentenceTransformer("all-MiniLM-L6-v2")

all_chunks = []
all_metadata = []

documents_folder = "documents"

for filename in os.listdir(documents_folder):

    if filename.endswith(".pdf"):

        pdf_path = os.path.join(documents_folder, filename)

        print(f"Loading: {filename}")

        pdf_text = load_pdf(pdf_path)

        chunks = chunk_text(pdf_text, chunk_size=500)

        for chunk in chunks:

            all_chunks.append(chunk)

            all_metadata.append(
                {
                    "text": chunk,
                    "source": filename
                }
            )


embeddings = model.encode(all_chunks)

embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(embeddings)

faiss.write_index(index, "faiss_index.bin")

with open("chunks.pkl", "wb") as f:
    pickle.dump(all_metadata, f)

print("\nTotal Chunks:", len(all_chunks))
print("Vectors stored:", index.ntotal)
print("FAISS index saved!")
print("Metadata saved!")