# search_chunks.py

import pickle

with open("chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

keyword = "Naija"

for i, chunk in enumerate(chunks):
    text = chunk["text"]

    if keyword.lower() in text.lower():
        print("\n====================")
        print("Chunk:", i)
        print(text[:1000])