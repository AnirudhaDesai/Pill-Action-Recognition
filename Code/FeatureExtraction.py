# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import FeatureExtractorUtils as fe

datafiles = np.load('all_data.npz')

id_data = np.asarray(datafiles['arr_0'])

N,L,T,D = id_data.shape # N- id, L-sensor location, T- sensor Type, D - dim



body_features = [fe.getMean, fe.getStdDev, fe.getMeadianAbsDev, fe.getMax,
                     fe.getMin, fe.getIQR, fe.getEntropy]
grav_features = [fe.getMean, fe.getStdDev, fe.getMeadianAbsDev, fe.getMax,
                 fe.getMin, fe.getIQR, fe.getEntropy]
freq_body_features = [fe.getMaxInds, fe.getMeanFreq, fe.getSkewness,
                     fe.getKurtosis]
dim_less_features = [fe.getSMA, fe.getEnergyMeasure]

num_features =  (len(body_features)+len(grav_features)+len(freq_body_features))\
                *L*T*D

features = np.empty((1,num_features))

for i in range(N):
    feature_row = np.empty((0,))
    for l in range(L):
        for t in range(T):
            #get sma , get energy measure
            
            for d in range(D):
                
                sdata = np.asarray(id_data[i][l][t][d])
                bComp = fe.getBodyAccelComponent(sdata)
                gComp = fe.getGravityAccelComponent(sdata)

                for bf in body_features:
#                    feature_row.append(bf(bComp))
                    feature_row = np.hstack((feature_row, bf(bComp)))
                    
                    
                for gf in grav_features:
#                    feature_row.append(gf(gComp))
                    feature_row = np.hstack((feature_row, gf(gComp)))
                
                fbody = fe.getFFT(np.real(bComp)) # freq domain 
                
                for bf in freq_body_features:
#                    feature_row.append(bf(fbody))
                    feature_row = np.hstack((feature_row, np.real(bf(fbody))))
    feature_row = np.asarray(feature_row)
    features = np.vstack((features, feature_row))
    
features = features[1:]
np.save('features.npy', features)    