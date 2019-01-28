"""
Copyright (c) 2018 Intel Corporation.
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:
The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.spatial.distance import cdist
from sklearn import cluster


def cal_Labels(files):
    """
    Generate the labels for supervised learning.
    Number of files for testset1 = 2148, testset2 = 984.
    
    :param files: No. of files in the dataset
    :return: labels
    """
    range_low = files*0.7
    range_high = files*1.0
    label = []
    for i in range(0,files):
        if(i<range_low):
            label.append(0)
        elif(i >= range_low and i <= range_high):
            label.append(1)
        else:
            label.append(2)
    return label


def cal_amplitude(fftData,n):
    """
    Process the fft data.
    
    :param fftData: fft value of each column for each file 
    :param n: No. of maximum amplitudes
    :return: Top 5 amplitude and their respective frequencies 
    """
    ifa = []
    ia = []
    amp = abs(fftData[0:int(len(fftData)/2)])
    freq = np.linspace(0,10000,num = int(len(fftData)/2))
    ida = np.array(amp).argsort()[-n:][::-1]
    ia.append([amp[i] for i in ida])
    ifa.append([freq[i] for i in ida])
    return(ifa,ia)

def cal_max_freq(files, path, no_of_bearings):
    """
    Calculates the top 5 frequencies which has the highest amplitude for each file.
    
    :param files: File present in the dataset
    :param path: Path of the dataset
    :param no_of_bearings: No. of bearings present in the dataset
    :return: List of 5 frequency components
    """
    print("Calculating the 5 frequency components for each file of ",path)
    freq_max1, freq_max2, freq_max3, freq_max4, freq_max5 = ([] for _ in range(5))
    print("\nProcessing... Please wait...\n")
    for f in files:
        temp = pd.read_csv(path+f,  sep = "\t",header = None)
        temp_freq_max1,temp_freq_max2,temp_freq_max3,temp_freq_max4,temp_freq_max5 = ([] for _ in range(5))

        for i in range(0, no_of_bearings):
            t = fft(temp[i])
            ff, aa = cal_amplitude(t,5)
            temp_freq_max1.append(np.array(ff)[:,0])
            temp_freq_max2.append(np.array(ff)[:,1])
            temp_freq_max3.append(np.array(ff)[:,2])
            temp_freq_max4.append(np.array(ff)[:,3])
            temp_freq_max5.append(np.array(ff)[:,4])
        freq_max1.append(temp_freq_max1)
        freq_max2.append(temp_freq_max2)
        freq_max3.append(temp_freq_max3)
        freq_max4.append(temp_freq_max4)
        freq_max5.append(temp_freq_max5)
    return(freq_max1,freq_max2,freq_max3,freq_max4,freq_max5)


def create_dataframe(freq_max1,freq_max2,freq_max3,freq_max4,freq_max5,bearing):
    """
    Create dataframe from the 5 frequency components.
    
    :param freq_max: Five dataframes of all the frequency components
    :return: DataFrame 
    """
    result = pd.DataFrame()
    result['fmax1'] = list((np.array(freq_max1))[:,bearing])
    result['fmax2'] = list((np.array(freq_max2))[:,bearing])
    result['fmax3'] = list((np.array(freq_max3))[:,bearing])
    result['fmax4'] = list((np.array(freq_max4))[:,bearing])
    result['fmax5'] = list((np.array(freq_max5))[:,bearing])
    x = result[["fmax1","fmax2","fmax3","fmax4","fmax5"]]
    return x


def elbow_method(X):
    """
    Used for choosing the no. of clusters in K-means algorithm.
    
    :param X: Dataframe
    :return: None
    """
    distortions = []
    K = range(1,10)
    for k in K:
        kmeanModel = cluster.KMeans(n_clusters = k).fit(X)
        kmeanModel.fit(X)
        distortions.append(sum(np.min(cdist(X, kmeanModel.cluster_centers_, 'euclidean'), axis = 1)) / X.shape[0])
    #  Plot the elbow
    plt.plot(K, distortions, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Distortion')
    plt.title('Elbow Method')
    plt.show()

