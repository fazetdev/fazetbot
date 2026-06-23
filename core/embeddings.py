from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

text = "Fazet Edu is a school management platform."

embedding = model.encode(text)

print("Embedding length:", len(embedding))
print(embedding[:5])