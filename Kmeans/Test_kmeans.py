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

import pandas as pd
import numpy as np
import os
import sys
import json
from influxdb import InfluxDBClient
from influxdb import DataFrameClient
sys.path.insert(0, '../')
from utils import create_dataframe


# Connecting to influxDb
influxdb1_client = InfluxDBClient("localhost", "8086", "admin","admin","Predictions_testset1")
influxdb1_client.create_database("Predictions_testset1")
influxdb2_client = InfluxDBClient("localhost", "8086", "admin","admin","Predictions_testset2")
influxdb2_client.create_database("Predictions_testset2")

dbname = input("Enter the database name: ")
    
if(dbname == '1st_test' or dbname == '2nd_test'):
    if (dbname=="1st_test"):
        no_of_bearings = 8
        influxdb_client = DataFrameClient("localhost", "8086", "admin","admin",dbname)
        
    elif(dbname == "2nd_test"):
        no_of_bearings = 4
        influxdb_client = DataFrameClient("localhost", "8086", "admin","admin", dbname)
    
    frequency_component1, frequency_component2, frequency_component3, frequency_component4, frequency_component5 = (pd.DataFrame() for _ in range(5))
    query = influxdb_client.query("select * from freq_comp")
    temporary_df = query['freq_comp']
    
    freq_dataframes = ['frequency_component1', 'frequency_component2', 
                       'frequency_component3', 'frequency_component4', 
                       'frequency_component5']
    testset_length = int(len(temporary_df)/5)
    for i , c in enumerate (freq_dataframes, 0):
        exec('{} = temporary_df.iloc[i*testset_length:i*testset_length+testset_length, : ]'.format(c,i))
        
    # Loading the test bearings
    with open('config.txt') as json_file:  
        data = json.load(json_file)
        for p in data['training_bearings']:
            if(no_of_bearings == 8):
                training_bearings = list(p['1st_test'])
            if(no_of_bearings == 4):
                training_bearings = list(p['2nd_test'])
                
    bearing_list = []
    for i in range(no_of_bearings):
        bearing_list.append(i)
        
    testing_bearings = list(np.setdiff1d(bearing_list,training_bearings))
    
    # Load the model
    filename = "kmeanModel.npy"
    model = np.load(filename).item()
    
    print("Testing ", dbname, "...")
    
    prediction_last_100 = []
    for k in testing_bearings:
        print("\nTesting bearing ",k+1)
        x = create_dataframe(frequency_component1, frequency_component2,
                             frequency_component3, frequency_component4,
                             frequency_component5,k)
    
        label = model.predict(x)   
        
        labelfour = list(label[-100:]).count(4)
        labelfive = list(label[-100:]).count(5)
        labelsix = list(label[-100:]).count(6)
        labelseven = list(label[-100:]).count(7)
        totalfailure = labelfive+labelsix+labelseven+labelfour
        ratio = (totalfailure/100)*100
        
        json_body = [
            {
                "measurement": "Kmeans",
                "tags": {
                    "type": "B"+str(k+1),
                },
                "fields": {
                    "failure_ratio": ratio,
                }
            }
            ]
        if (no_of_bearings == 8):
            influxdb1_client.write_points(json_body)
        else:
            influxdb2_client.write_points(json_body)    
    
        if(ratio >= 25):
            print("Bearing " + str(k+1) +" is suspected to fail!")
        else:
            print("Bearing " + str(k+1) + " is working normally.")
    
        prediction_last_100.append(label[-100:])    
else:
    print("Invalid Database name")
    exit()

