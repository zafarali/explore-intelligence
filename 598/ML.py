import numpy as np

def mean_squared_error(X,Y, W):
	"""
		Evaluates the error due to given weights W.
	"""
	A = Y-X*W
	return (A.T * A)[0]

def derivative_of_squared_error(X,Y,W):
	return -2 * X.T * (Y - X*W)



def add_bias_term(data):
	bias_term = np.ones( ( data.shape[0] , 1 ) )
	return np.matrix( np.append(bias_term, data, axis =1 ) )

def least_squares(X, Y):
	"""
		Computes the weights of a hypothesis using the least squares method
	"""
	return np.linalg.inv(X.T * X)  * (X.T * Y)

def gradient_descent(X,Y, start_weights=False, error_function=derivative_of_squared_error, max_iterations=10, alpha=0.05, return_ws=False):
	"""
		Computes the weights of a hypothesis using the gradient descent method.
	"""
	number_of_weights = X.shape[1]
	if type(start_weights) != bool:
		w = start_weights
	else:
		w = np.matrix(np.random.random(size=number_of_weights)).T
		

	w_iterated = [w]
	for k in range(max_iterations):
		w_new = w - alpha * error_function(X,Y,w) # calculate new w.
		w_iterated.append(w_new)
		w = w_new
	if return_ws:
		return w, w_iterated
	else:
		return w

class Hypothesis(object):
	@staticmethod
	def linear(weights):
		"""
			returns a function that can be evaluated using X to obtain y
		"""
		def h(X):
			
			return np.array(add_bias_term(X) * weights)
		return h