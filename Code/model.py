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
from sklearn.neighbors import KNeighborsClassifier as KNN
import pickle

DIRECTORY = '../misc/test_bed_all/'
TEST_SAMPLES = 20
TRAINING_MODEL = 'Ensemble' # other option is 'Binary', decides which model is being trained
CLASS_TO_BE_TESTED = 1 # For binary model keep 1, otherwise it represents which action you want to train for
ITERATIONS = 500

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
    
def get_test_train_idx(total, test = 30):
    idx_test = np.random.choice(np.arange(0, total), size = test, replace=False)
    idx_test = np.sort(idx_test)
    idx_train = np.array([i for i in range(0, total) if i not in idx_test])
    return idx_train, idx_test

def getdata(wear=True, base=True, cap=False):
    Y = np.load(DIRECTORY + 'new_all_data.npz')['arr_1']
    path = DIRECTORY
    endpath = 'features.npy'
    if base == True:
        path += 'base_'
    if cap == True:
        path += 'cap_'
    if wear == True:
        path += 'wear_'
    X = np.load(path + endpath)
    return X, Y
    

if __name__ == '__main__':  
    X, Y = getdata(wear=True, base=True, cap=False)
    X[np.isinf(X)] = 0.0
    cls = CLASS_TO_BE_TESTED
    
    Y = (Y == cls)*1.0
    
    iterations = ITERATIONS
    models = {LinearSVC(): 'Linear SVM', SVC(kernel='sigmoid'): 'Sigmoid SVM', RFC(): 'Random Forest', 
              logreg(): 'Logistic Regression', dtree(): 'Decision Tree', newmodel(): 'True Random',
              newmodel(a=0): 'Always Zero', newmodel(a=1): 'Always One', KNN(n_neighbors=3): 'KNN'}
    
    best_model = None
    best_acc = 0
    for model in models:
        print('Testing Model - ', models[model])
        avg_acc = 0
        avg_fp = 0.0
        for it in range(0, iterations):
            # The commented code below is what I used to counter imbalanced data classes
            # keeping it here in case it's needed for reference. Though we do have version control
            # so don't know the point. You will probably need to account for class imbalance in case of training the ensemble.
#            yidxf = np.arange(0, len(Y))[Y==0]
#            yidxt = np.arange(0, len(Y))[Y==1]
#            
#            yidxf = np.random.choice(yidxf, size=43, replace=False)
#            
#            Y_ = [Y[yidxf[i]] for i in range(len(yidxf))] + [Y[yidxt[i]] for i in range(len(yidxt))]
#            Y_ = np.array(Y_)
#            
#            X_ = [X[yidxf[i]] for i in range(len(yidxf))] + [X[yidxt[i]] for i in range(len(yidxt))]
#            X_ = np.array(X_)
            
            X_ = X
            Y_ = Y
            
            idx_train, idx_test = get_test_train_idx(X_.shape[0], TEST_SAMPLES)
            
            X_test = X_[idx_test]
            Y_test = Y_[idx_test]
            
            X_train = X_[idx_train]
            Y_train = Y_[idx_train]
            model.fit(X_train, Y_train)
            pred = model.predict(X_test)
            acc = np.mean(pred == Y_test)
            fp = np.sum(pred[Y_test == 0])/len(pred)
            avg_acc += acc
            avg_fp += fp
            #print('Iter = ', it, ' Acc = ', acc, 'False positives = ', fp)
        print('Avg Accuracy for ', models[model], ' = ', avg_acc/iterations, 'Avg False Positives = ', avg_fp/iterations)
        if (avg_acc > best_acc):
            best_acc = avg_acc
            best_pred = pred
            best_fp = avg_fp/iterations
            best_model = model
    
    print('The best model is ', models[best_model], ' avg cross-val acc = ', best_acc/iterations, ' fp  =', best_fp)
    #best_model.fit(X, Y)
    print('Best Acc = ', np.mean(best_model.predict(X) == Y))
    best_model.fit(X, Y) # fit with all data before saving model, no data goes to waste!! 
    
    
    if TRAINING_MODEL == 'Ensemble':
        if cls == 0:
            pickle.dump(best_model, open('../model/m_twist.pkl', 'wb'))
        elif cls == 1:
            pickle.dump(best_model, open('../model/m_dispense.pkl', 'wb'))
        elif cls == 2:
            pickle.dump(best_model, open('../model/m_h2m.pkl', 'wb'))
        else:
            pickle.dump(best_model, open('../model/m_w2m.pkl', 'wb'))
    elif TRAINING_MODEL == 'Binary':
        pickle.dump(best_model, open('../model/binary_classifier.pkl', 'wb'))

