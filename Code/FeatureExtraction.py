# -*- coding: utf-8 -*-
"""
Created long, long ago in a land far, far away.

"""
import numpy as np
import FeatureExtractorUtils as fe

def extract_features(id_data):
    #print (id_data.shape)
    N,L,T,D = id_data.shape # N- id, L-sensor location, T- sensor Type, D - dim
    print ("Feature Extraction initiated ... ")
    
    body_features = [fe.getMean, fe.getStdDev, fe.getMeadianAbsDev, fe.getMax,
                    fe.getMin, fe.getIQR, fe.getEntropy,fe.getEnergyMeasure
                    ]
    grav_features = [fe.getMean, fe.getStdDev, fe.getMeadianAbsDev, fe.getMax,
                     fe.getMin, fe.getIQR, fe.getEntropy]
    freq_body_features = [fe.getMaxInds, fe.getMeanFreq, fe.getSkewness,
                         fe.getKurtosis]
    dim_less_features = [fe.getSMA, fe.getEnergyMeasure]
    
    num_features =  (len(body_features)+len(grav_features)+len(freq_body_features))\
                    *L*T*D
    uni_features =  (len(body_features)+len(grav_features)+len(freq_body_features))\
                    *T*D
    features = np.empty((1,num_features))
    wear_features = np.empty((1,uni_features))
    base_features = np.empty((1,uni_features))
    cap_features =  np.empty((1,uni_features))
    
    try:
        for i in range(N):
            feature_row = np.empty((0,))
            for l in range(L):
                sub_features = np.empty((0,))
                #print ('for sensor : ', l)
                for t in range(T):
                    #get sma , get energy measure
                    
                    for d in range(D):
        #                print(id_data[i][l][t][d])
                        sdata = np.asarray(id_data[i][l][t][d])
                        bComp = fe.getBodyAccelComponent(sdata)
                       
                        
                        gComp = fe.getGravityAccelComponent(sdata)
        
                        for bf in body_features:
        #                    feature_row.append(bf(bComp))
                            feature_row = np.hstack((feature_row, bf(bComp)))
                            sub_features = np.hstack((sub_features, bf(bComp)))
                            
                            
                        for gf in grav_features:
        #                    feature_row.append(gf(gComp))
                            feature_row = np.hstack((feature_row, gf(gComp)))
                            sub_features = np.hstack((sub_features, gf(gComp)))
                            
                        
                        fbody = fe.getFFT(np.real(bComp)) # freq domain 
                        
                        for bf in freq_body_features:
        #                    feature_row.append(bf(fbody))
                            feature_row = np.hstack((feature_row, np.real(bf(fbody))))
                            sub_features = np.hstack((sub_features, np.real(bf(fbody))))
                if l == 0:
                    base_features = np.vstack((base_features, sub_features))
                elif l == 1:
                    cap_features = np.vstack((cap_features, sub_features))
                elif l == 2:
                    wear_features = np.vstack((wear_features, sub_features))
            feature_row = np.asarray(feature_row)
            features = np.vstack((features, feature_row))
    except Exception as e:
        print ("Error in feature extraction : ", e)
        return None
        
     
    features = features[1:]
    base_features = base_features[1:]
    cap_features = cap_features[1:]
    wear_features = wear_features[1:]
    base_wear_features = np.vstack((base_features, wear_features))
    cap_wear_features = np.vstack((cap_features, wear_features))
    print ("Feature extraction complete..", cap_wear_features)  
    return (features, base_features, 
            cap_features, 
            wear_features, 
            base_wear_features,
            cap_wear_features)


if __name__ == '__main__':
    
    path = '../misc/test_bed_all/'
    
    datafiles = np.load(path + 'new_all_data.npz')
    
    print('Loaded file')
    id_data = np.asarray(datafiles['arr_0'])
    features, base_features, cap_features, wear_features, cap_wear_features, base_wear_features = extract_features(id_data)
    
    print('Saving Files..')  
    
    np.save(path + 'base_cap_wear_features.npy', features)    
    np.save(path + 'base_features.npy', base_features)
    np.save(path + 'cap_features.npy', cap_features)
    np.save(path + 'wear_features.npy', wear_features)
    np.save(path + 'cap_wear_features.npy', cap_wear_features)
    np.save(path + 'base_wear_features.npy', base_wear_features)
