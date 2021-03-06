# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 12:38:41 2018

@author: amitrc
"""

import numpy as np
from sklearn.svm import SVC
from sklearn.svm import LinearSVC as LinearSVC
from sklearn.linear_model import LogisticRegression as logreg
from sklearn.tree import DecisionTreeClassifier as dtree
from sklearn.ensemble import RandomForestClassifier as RFC
import featureSelect as fs

class newmodel:
    
    def __init__(self, a = None):
        self.pred = a
        pass
    
    def fit(self, X, Y):
        pass
    
    def predict(self, X):
        if self.pred == None:
            return np.random.randint(0, 2, X.shape[0])
        else:
            return np.zeros(X.shape[0]) + self.pred
    
def get_test_train_idx(total, test = 100):
    idx_test = np.random.choice(np.arange(0, total), size = test, replace=False)
    idx_test = np.sort(idx_test)
    idx_train = np.array([i for i in range(0, total) if i not in idx_test])
    return idx_train, idx_test
 
X = np.load('../misc/cap_wear_features.npy')
Y = np.load('../misc/new_all_data.npz')['arr_1']
cls = 3 # Class to be tested

Y = (Y == cls)*1.0


iterations = 20
#models = {LinearSVC(): 'Linear SVM', SVC(kernel='sigmoid'): 'Sigmoid SVM', RFC(): 'Random Forest', 
#          logreg(): 'Logistic Regression', dtree(): 'Decision Tree', newmodel(): 'True Random',
#          newmodel(a=0): 'Always Zero', newmodel(a=1): 'Always One'}
models = {RFC():'Random Forest Classifier'}

best_model = None
best_acc = 0
for model in models:
    print('Testing Model - ', models[model])
    avg_acc = 0
    avg_fp = 0.0
    for it in range(0, iterations):
        idx_train, idx_test = get_test_train_idx(X.shape[0], 100)
        
        X_test = X[idx_test]
        Y_test = Y[idx_test]
        
        X_train = X[idx_train]
        Y_train = Y[idx_train]
        model.fit(X_train, Y_train)
        pred = model.predict(X_test)
        acc = np.mean(pred == Y_test)
        fp = np.sum(pred[Y_test == 0])/len(pred)
        avg_acc += acc
        avg_fp += fp
        print('Iter = ', it, ' Acc = ', acc, 'False positives = ', fp)
    print('Avg Accuracy for ', models[model], ' = ', avg_acc/iterations, 'Avg False Positives = ', avg_fp/iterations)
    if (avg_acc > best_acc):
        best_acc = avg_acc
        best_model = model

print('The best model is ', models[best_model], ' acc = ', best_acc/iterations)