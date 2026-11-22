from sentence_transformers import SentenceTransformer
from sentence_transformers import util

# Load pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

sentance1 = "Python is a programming language"
sentance2 = "Python is used for software development"

embedding1 = model.encode(sentance1,convert_to_tensor=True)
embedding2 = model.encode(sentance2,convert_to_tensor=True)

# Calculate cosine similarity
similarity = util.cos_sim(embedding1,embedding2)

print("Sentance 1 : ",sentance1)
print("Sentance 2 : ",sentance2)

print("Cosine Similarity : ")
print(similarity.item())