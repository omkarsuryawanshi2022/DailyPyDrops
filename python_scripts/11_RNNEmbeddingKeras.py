from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding
import numpy as np

sentences = [
    "food was good",
    "food was bad",
    "food was not good"
    ]

tokenizer = Tokenizer()

tokenizer.fit_on_texts(sentences)

sequances = tokenizer.texts_to_sequences(sentences)

max_length = 4

X = pad_sequences(
    sequances,
    maxlen = max_length,
    padding = "pre"
)

vocab_size = len(tokenizer.word_index) + 1

embedding_model = Sequential()
embedding_model.add(Embedding(input_dim=vocab_size, output_dim=4))
embedding_model.build(input_shape = (None,max_length))

embedding_model.summary()

embedding_output = embedding_model.predict(X,verbose = 0)

print("Embedding vector for first sentance")
print("Sentance : ",sentences[0])
print("Padded sequance : ",X[0])

for position,token in enumerate(X[0]):
    print("Position : ",position+1)
    print("Token : ",token)
    print("Vector : ",np.round(embedding_output[0][position], 4))