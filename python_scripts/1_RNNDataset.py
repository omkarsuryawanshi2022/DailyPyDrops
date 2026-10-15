sentences = [
    "food was good",
    "food was bad",
    "food was not good"
]

labels = [1,0,0]

for sentance , label in zip(sentences,labels):
    sentiment = "Positive" if label == 1 else "Negative"

    print("Sentance : ",sentance)
    print("Label : ",label)
    print("Meaning : ",sentiment)
    print("------------------------------")