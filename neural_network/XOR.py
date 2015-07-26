from sknn.mlp import Classifier, Layer
import numpy as np

# create a classifier
nn = Classifier(
  layers = [
    Layer("Rectifier", units=100),
    Layer("Softmax")
  ],
  learning_rate = 0.2,
  n_iter=100,
  verbose=True)

X_train = np.array([ (0, 0), (0, 1), (1, 1), (1,0) ])
y_train = np.array([ 0, 1, 0, 1 ])

nn.fit(X_train, y_train)


X_example = np.array([ (1, 1), (0, 1), (0, 0), (1, 0) ])
y_example = nn.predict(X_example)

print y_example
