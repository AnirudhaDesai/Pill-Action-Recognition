#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:48:16 2018

@author: anirudha
"""

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.feature_selection import VarianceThreshold


def kBest(X,Y,k=10):
    
    return SelectKBest(chi2, k).fit_transform(X,Y)

def VarThreshold(X, var = 0.7):
    sel = VarianceThreshold(threshold = (var*(1-var)))
    X_new = sel.fit_transform(X)
    print ('After feature Selection : ', X_new.shape)
    return X_new


    