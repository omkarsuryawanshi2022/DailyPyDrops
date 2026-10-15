# ht = tanh(Wx * Xt + Wh * ht-1 + b)

# Xt        Current input
# Wx        Weight of current input
# Wh        Weight of previous hiddent state
# b         Bias
# ht-1      Previous hideen state
# tanh      Activation function (-1 to 1)
# ht        New hidden state

import numpy as np

def sigmpoid(x):
    return 1 / (1 + np.exp(-x))

def MarvellousRNNPredictions():
    print("Claculation of RNN")

    # food was not good
    inputs = [1,2,5,3]

    hidden_state = 0

    # RNN parameters
    Wx = 0.5
    Wh = 0.8
    bias = 0.1

    # RNN Calculation
    for time_step, x in enumerate(inputs):
        previous_hidden_state = hidden_state

        weighted_input = Wx * x
        weighted_memory = Wh * previous_hidden_state

        total = weighted_input + weighted_memory + bias

        hidden_state = np.tanh(total)

        print("Time Step : ",time_step+1)
        print("Input : ",x)
        print("Hidden State : ",hidden_state)
        print("-"*30)

    # Step : 2 - Final Hidden State
    print("Final Hidden State : ",hidden_state) 

    # Step 3 : Output layer
    # Output = Wy * FinalHiddenState + Output Bias

    Wy = 1.0
    output_bias = 0.0

    output = (Wy * hidden_state) + output_bias

    print("Raw Output : ",output)

def main():
    MarvellousRNNPredictions()

if __name__ == "__main__":
    main()