# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 12:38:41 2018

@author: amitrc
"""

import numpy as np
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier


Y = np.load('all_data.npz')['arr_1']
X = np.load('features.npy')

cls = 3 # Class to be tested

Y = np.load('../data/all_data.npz')['arr_1']
X = np.load('../data/features.npy')
X[np.isinf(X)] = 0.0
cls = 1 # Class to be tested


Y = (Y == cls)*1.0

idx_test = np.random.randint(0, 60, size=20)
idx_test = np.sort(idx_test)
X_test = X[idx_test]
Y_test = Y[idx_test]

idx_train = [i for i in range(0, 60) if i not in idx_test]

X_train = X[idx_train]
Y_train = Y[idx_train]
model = SVC(kernel='linear')
model.fit(X_train, Y_train)
pred = model.predict(X_test)
print('Acc = ', np.mean(pred == Y_test))

model2 = RandomForestClassifier()
model2.fit(X_train,Y_train)
pred = model2.predict(X_test)
print('RFCAcc = ', np.mean(pred == Y_test))