## Information theory functions
import numpy as np

def information_content(p):
    """ Calculates the information content represented by the probability p """
    return np.log2(1/float(p))

def entropy(P):
    """ Calculates the Entropy of the (discrete) probability distribution P """
    return np.sum([ p * information_content(p) for p in P])

def dataset_entropy(D):
    """ Calculates the Entropy of a dataset
        @params:
        D: the dataset containing only the labels
    """
    D = np.array(D)
#     print D
    labels = np.unique(D)
#     print labels
#     print(labels)
    probabilities = np.zeros( len(labels) )
    
    # enumerate over all the labels and conduct some counting
    for label_index, label in enumerate(labels):
        probabilities[label_index] = np.sum(label == D)
    
    #divide by length of the dataset to get the probability of that class 
    probabilities = probabilities/float(len(D))
#     print probabilities
    # return the entropy of the probability distribution
    return entropy(probabilities)


# our metric for determining which tests are good.
def information_gain(D, T):
    """
        Calculates the information gain given by this test
    """    
    D = np.array(D)
    observations = D.T[-1].T
    return dataset_entropy(observations) - test_entropy(D, T)

def test_entropy(D, T):
    """
        Calculates the entropy of a dataset D due to test T
        @params:
            D: dataset containing observations [(x_11,..., x_1m, y_1), ..., (x_n1, ..., x_nm, y_n)]
            T: test to apply on the features
    """
    # first vectorize the test.
    D = np.array(D)
    
    #seperate observations and labels into their own arrays so that the test cannot access the label itself.
    observations, labels = D.T[0:-1].T, D.T[-1].T

    test_passed = np.apply_along_axis(T ,axis=1,arr=observations)

    # whats the probability that a datapoint passes a test?
    P_test_passed = np.sum(test_passed)/float(len(D))
    P_test_failed = 1 - P_test_passed
    
    
    # what are the labels that passed the test?
    labels_test_passed = labels[ test_passed ]
    labels_test_failed = labels[ np.invert(test_passed) ]
    
    # what is the entropy of the resulting datasets?
    entropy_test_passed = dataset_entropy(labels_test_passed)
    entropy_test_failed = dataset_entropy(labels_test_failed)

    # return the entropy of the dataset given the test
    return P_test_passed * entropy_test_passed + P_test_failed * entropy_test_failed