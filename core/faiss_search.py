import faiss
import pickle
import numpy as np

from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


index = faiss.read_index("faiss_index.bin")

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)


question = input("Ask a question: ")


question_embedding = model.encode([question])

question_embedding = np.array(question_embedding).astype("float32")


distances, indices = index.search(question_embedding, 3)


print("\nTop Matches:\n")

for i in indices[0]:
    print("=" * 50)
    print(chunks[i])