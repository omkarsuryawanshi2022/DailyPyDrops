###############################################
# Step 1 : Import required libraries
###############################################

from tensorflow.keras.datasets import imdb
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.sequence import pad_sequences

###############################################
# Step 2 : Configuration of values
###############################################

VOCAB_SIZE = 10000  # consider most frequent 10000 unique words
MAX_LENTH = 200     # consider maximum 200 words in review

###############################################
# Step 3 : Load the IMDB dataset
###############################################

print("-"*40)
print("Movie Review Sentiment Analysis using LSTM")
print("-"*40)

print("Loading the dataset...")

(X_train, Y_train), (X_test, Y_test) = imdb.load_data(num_words = VOCAB_SIZE)

print("IMDB dataset loaded succesfully")

print("Number of training reviews : ",len(X_train))
print("Number of testing reviews : ",len(X_test))

###############################################
#   X_train     Reviews used for training
#   Y_train     Actual sentiements of training
#   X_test      Reviews used for testing
#   Y_test      Actual sentiments of testing

# Sentiments : 
# 0 -> Negative sentiment
# 1 -> Positive sentiment
###############################################

###############################################
# Step 4 : Load the word dictonary
###############################################

word_index = imdb.get_word_index()

# Dictonary contains mapping of word and its correspoding number
# drisham is good movie     ->  (20 56 78 43)
# 20    ->  drisham
# 56    ->  is
# 78    ->  good
# 43    ->  movie

###############################################
# Step 5 : Create reverse dictonary
###############################################

reverse_word_index = {}

for word,index in word_index.items():
    reverse_word_index[index+3] = word

###############################################
# Step 6 : Function to decode the review (number to word)
###############################################

def DecodeReview(encoded_review):
    words = []

    for number in encoded_review:
        if number >= 3: # ignore first 3
            word = reverse_word_index.get(number,"?")   
            words.append(word)

    return " ".join(words)  # join the list of words

###############################################
# Step 7 : Display sample review
###############################################

print("-"*40)
print("--------- Sample Reviews ---------")
print("-"*40)

for i in range(3,7):
    review = DecodeReview(X_train[i])

    print("-"*40)

    print("Review number : ",i+1)
    print("Review : ")
    print(review)
    
    print("-"*40)

    if Y_train[i] == 1:
        print("Sentiment : POSITIVE")
    else:
        print("Sentiment : NEGATIVE")

