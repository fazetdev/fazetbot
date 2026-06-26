import pickle

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

print(f"Total chunks: {len(chunks)}")

for i, chunk in enumerate(chunks[:10]):
    print("\n" + "-" * 50)
    print(f"Chunk {i}")
    print(chunk)