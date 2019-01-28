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
from scipy.fftpack import fft
import os


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
    freq_comp1, freq_comp2, freq_comp3, freq_comp4, freq_comp5 = ([] for _ in range(5))
    print("\nProcessing... Please wait...\n")
    for f in files:
        temp = pd.read_csv(path+f,  sep = "\t",header = None)
        temp_freq_comp1,temp_freq_comp2,temp_freq_comp3,temp_freq_comp4,temp_freq_comp5 = ([] for _ in range(5))

        for i in range(0,no_of_bearings):
            t = fft(temp[i])
            ff, aa = cal_amplitude(t,5)
            temp_freq_comp1.append(np.array(ff)[:,0])
            temp_freq_comp2.append(np.array(ff)[:,1])
            temp_freq_comp3.append(np.array(ff)[:,2])
            temp_freq_comp4.append(np.array(ff)[:,3])
            temp_freq_comp5.append(np.array(ff)[:,4])
        freq_comp1.append(temp_freq_comp1)
        freq_comp2.append(temp_freq_comp2)
        freq_comp3.append(temp_freq_comp3)
        freq_comp4.append(temp_freq_comp4)
        freq_comp5.append(temp_freq_comp5)
        
    final_freq_comp = [freq_comp1, freq_comp2,freq_comp3, freq_comp4, freq_comp5]
    list_final = []
    i = 0
    j = 0
    k = 0
    for i in final_freq_comp:
        sum1 = []
        sum1= (sum(i, []))
        sum2=[]
        for j in range (0,len(sum1)):
            sum2.append(float(sum1[j][0]))
        list_final = ([sum2[k:k+no_of_bearings] for k in range(0, len(sum2), no_of_bearings)])
        #list_final.append(final)
        df = pd.DataFrame(list_final)
        if (no_of_bearings == 8):
            df.to_csv('1st_test.csv', mode = 'a', index = False, header = False)
        elif (no_of_bearings == 4):
            df.to_csv('2nd_test.csv', mode = 'a', index = False, header = False)


def main():
    # Removing the already existing files
    if os.path.exists("1st_test.csv" and "2nd_test.csv"):  
        os.remove("1st_test.csv")
        os.remove("2nd_test.csv")
    # Reading all the files from testset1 and testset2
    filedir_testset1 = input("Enter the path to the data set, 1st_test: ")
    filedir_testset2 = input("Enter the path to the data set, 2nd_test: ")
    
    if (os.path.exists("1st_test/" and "2nd_test/") and (filedir_testset1 == '1st_test/' and filedir_testset2 == '2nd_test/')):
        all_files_testset1 = os.listdir(filedir_testset1)
        all_files_testset2 = os.listdir(filedir_testset2)              
        bearing_1st_test = 8
        bearing_2nd_test = 4    
        cal_max_freq(all_files_testset1, filedir_testset1, bearing_1st_test )
        cal_max_freq(all_files_testset2, filedir_testset2, bearing_2nd_test)
    else:
        print("File does not exist or invalid path of the data set!")
        exit()


if __name__  == "__main__":
  main()

