"""
	This is a toy demonstration of a neural network that learns
	two functions simultaneously: 
		(1) Count the number of ones
		(2) Count the number of zeros

	appearing in a binary sequence of length 3.

	We frame this as a categorical task as this is what is most closely
	related to our end goal

	@author: zafarali
"""

from keras import layers
from keras.models import Model
from keras.utils.np_utils import to_categorical
import numpy as np


"""
	Some training examples. I have purposefully left out [0, 1, 0]
	as an unseen test case.
"""

data = np.array([
					[0, 0, 0],
					[1, 0, 0],
					[0, 0, 1],
					[1, 0, 1],
					[0, 0, 0],
					[1, 0, 1],
					[0, 1, 1],
					[1, 1 ,1],
					[1, 1, 1],
					[0, 0, 0],
					[1, 1, 0]	
				])

"""
	Correct labels
"""
count_of_ones = np.array([0, 1, 1, 2, 0, 2, 2, 3, 3, 0, 2])
count_of_zeros = 3 - count_of_ones
to_predict = [
	to_categorical(count_of_ones),
	to_categorical(count_of_zeros)
]


"""
	Model specification
"""
input_layer = layers.Input(shape=(3,), name='input')
hidden_layer = layers.Dense(units=10, name='hidden1', activation='relu')(input_layer)
hidden_layer = layers.Dense(units=10, name='hidden1', activation='relu')(input_layer)
hidden_layer = layers.Dense(units=10, name='hidden2', activation='tanh')(hidden_layer)

"""
	Using the Model() functional API it is easy for us to get two separate outputs.
"""
output_layers = []
output_layers.append(layers.Dense(units=4, activation='softmax', name='num_zeros')(hidden_layer))
output_layers.append(layers.Dense(units=4, activation='softmax', name='num_ones')(hidden_layer))

model = Model(inputs=input_layer, outputs=output_layers)
model.compile(optimizer='adam', loss='categorical_crossentropy')
print(model.summary())
model.fit(data, to_predict, verbose=1, validation_split=0.1, epochs=200)


"""
	Metrics
"""
train_preds = model.predict(data)


def to_label(vector):
	return np.argmax(vector, axis=1)

print('number of ones predicted:')
print(to_label(train_preds[0]))

print('number of ones expected:')
print(count_of_ones)


print('number of zeros predicted:')
print(to_label(train_preds[1]))

print('number of zeros expected:')
print(count_of_zeros)


print('Does it generalize?')
preds = model.predict(np.array([[1,0,0]]))
print('How many ones in [1, 0, 0]?')
print(to_label(preds[0]))
print('How many zeros in [1, 0, 0]?')
print(to_label(preds[1]))

preds = model.predict(np.array([[0,1,0]]))
print('How many ones in [0, 1, 0]?')
print(to_label(preds[0]))
print('How many zeros in [0, 1, 0]?')
print(to_label(preds[1]))

preds = model.predict(np.array([[0,0,1]]))
print('How many ones in [0, 0, 1]?')
print(to_label(preds[0]))
print('How many zeros in [0, 0, 1]?')
print(to_label(preds[1]))

preds = model.predict(np.array([[0,0,0]]))
print('How many ones in [0, 0, 0]?')
print(to_label(preds[0]))
print('How many zeros in [0, 0, 0]?')
print(to_label(preds[1]))
