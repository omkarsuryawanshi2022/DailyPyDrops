sentences = [
    "food was good",
    "food was bad",
    "food was not good"
]

vocabulary = []

for sentance in sentences:
    words = sentance.split()

    for word in words:
        if word not in vocabulary:
            vocabulary.append(word)

for index, x in enumerate(vocabulary):
    print("Position ",index+1, ":",x)
    