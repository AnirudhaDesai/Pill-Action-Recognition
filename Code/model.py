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

def get_test_train_idx(total, test = 100):
    idx_test = np.random.randint(0, total, test)
    idx_train = [i for i in range(0, total) if i not in idx_test]
    return idx_train, idx_test

X = np.load('../data/new_features.npy')
Y = np.load('../data/new_all_data.npz')['arr_1']
cls = 2 # Class to be tested
Y = (Y == cls)*1.0


iterations = 20
models = {LinearSVC(): 'Linear SVM', SVC(kernel='sigmoid'): 'Sigmoid SVM', RFC(): 'Random Forest', 
          logreg(): 'Logistic Regression', dtree(): 'Decision Tree'}

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