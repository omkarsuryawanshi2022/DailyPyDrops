from sentence_transformers import SentenceTransformer

# Load pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

sentances = [
    "Python is a programming language",
    "Python is used for data science",
    "I support indian crickt team"
]

embeddings = model.encode(sentances)

# Display sentance embeddings
for index, embedding in enumerate(embeddings):
    print("-"*40)
    print("\nSentance : ",sentances[index])

    print("Embedding : ")
    print(embedding[:10])

    print("Total dimention : ",len(embedding))