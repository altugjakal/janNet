import numpy as np
import pandas as pd

def load_dataset():
    train_set_x_orig = pd.read_csv("./csv/model/keyword_training_x.csv", header=None).values
    train_set_y_orig = pd.read_csv("./csv/model/keyword_training_y.csv", header=None).values
    test_set_x_orig = pd.read_csv("./csv/model/keyword_testing_x.csv", header=None).values
    test_set_y_orig = pd.read_csv("./csv/model/keyword_testing_y.csv", header=None).values
    
    
    train_set_y_orig = train_set_y_orig.reshape((1, train_set_y_orig.shape[0]))
    test_set_y_orig = test_set_y_orig.reshape((1, test_set_y_orig.shape[0]))
    
    return train_set_x_orig, train_set_y_orig, test_set_x_orig, test_set_y_orig



def sigmoid(z):
    s = 1/(1 + np.exp(-1*z))
    return s

def initialize_with_zeros(dim):

    w = np.zeros((dim, 1))
    b = 0.0
    
  

    return w, b

def predict(w, b, X):
    m = X.shape[1]
    Y_prediction = np.zeros((1, m))
    w = w.reshape(X.shape[0], 1)

    A = sigmoid(np.dot(w.T, X) + b)

    for i in range(A.shape[1]):
        if A[0, i] > 0.5:
            Y_prediction[0, i] = 1
        else:
            Y_prediction[0, i] = 0
    
    return Y_prediction

def propagate(w, b, X, Y):
    m = X.shape[1]
    A = sigmoid(np.dot(w.T, X) + b)
    cost = -1/m * np.sum(Y * np.log(A) + (1-Y) * np.log(1-A))

    dw = 1/m * np.dot(X, (A-Y).T)
    db = 1/m * np.sum(A-Y)

    cost = np.squeeze(np.array(cost))

    
    grads = {"dw": dw,
             "db": db}
    
    return grads, cost

def optimize(X,Y, w, b, iterations, lr):

    costs = []

    for i in range(iterations):

        grads, cost = propagate(w, b, X, Y)

        dw = grads['dw']
        db = grads['db']

        w = w -lr * dw
        b = b -  lr * db

        costs.append(cost)

    params = {"w": w,
              "b": b}
    
    grads = {"dw": dw,
             "db": db}
    
    return params, grads, costs

def model(X_train, Y_train, X_test, Y_test, iterations, lr):
    w, b = initialize_with_zeros(X_train.shape[0])
    
    params, grads, costs = optimize(X_train, Y_train, w, b, iterations, lr)
    w = params["w"]
    b = params["b"]
    

    
    
    Y_prediction_test = predict(w, b, X_test)
    Y_prediction_train = predict(w, b, X_train)