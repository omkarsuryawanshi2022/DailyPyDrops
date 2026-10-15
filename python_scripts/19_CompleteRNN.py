import numpy as np

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, SimpleRNN, Dense

# Step 1 : Load the data

train_setnatces = [
    "food was good",
    "food was bad",
    "food was excellent",
    "food was terrible",
    "service was good",
    "serice was bad",
    "service was excellent",
    "service was terrible",
    "ambience was good",
    "ambience was bad",
    "ambience was excellent",
    "ambience was terrible"
]

train_labels = [
    1,
    0,
    1,
    0,
    1,
    0,
    1,
    0,
    1,
    0,
    1,
    0
]

# Step 2 : Tokenisation

tokenizer = Tokenizer(oov_token = "<OOV>")

tokenizer.fit_on_texts(train_setnatces)

# Step 3 : Convert training data into sequance

train_sequance = tokenizer.texts_to_sequences(train_setnatces)

print("Training sequances : ")

for sentance, sequance in zip(train_setnatces,train_sequance):
    print(sentance, " -> ", sequance)

# Step 4 : Apply padding

max_length = 4

X_train = pad_sequences(
    train_sequance,
    maxlen = max_length,
    padding = "pre"
)

Y_train = np.array(train_labels)

print("Padded training data")
print(X_train)

print("Training labels : ")
print(Y_train)