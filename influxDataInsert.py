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

"""
This script is called from the OPC-UA client for bulk 
insertion of the data received from OPC-UA server in 
InfluxDB.
"""
import datetime
import json
import os.path
import signal
import sys
import time
from influxdb import InfluxDBClient

bool_variable=True


def signal_handler(signal, frame):
    """
    :param signal: Ctrl+C
    :return: None
    """
    global bool_variable
    print("You pressed Ctrl+C!")
    bool_variable = False
    sys.exit(0) 


if __name__ == "__main__":
    # catch ctrl-c
    signal.signal(signal.SIGINT, signal_handler)

    host = "localhost"
    port = 8086
    user = "root"
    password = "root"
    query = 'select count(Bearing_1) from freq_comp'
    json_data = []
    currdate = datetime.datetime.now()
    counter = 0

    with open(sys.argv[1]) as fp:
        noOfColumns = len(fp.readline().split())
        fp.seek(0,0)
        for line in fp:
            temp = {}
            temp["measurement"] = "freq_comp"
            currdate = currdate + datetime.timedelta(minutes=10)
            temp["time"] = currdate.isoformat()
            fieldArray = line.split()
            temp["fields"] = {}
            for columnNo in range(noOfColumns):
                bearingNo = "Bearing_" + str(columnNo+1)
                temp["fields"][bearingNo] = float(fieldArray[columnNo])
            json_data.append(temp)
            counter = counter + 1

    dbname = "1st_test" if (noOfColumns == 8) else "2nd_test"

    client = InfluxDBClient(host, port, user, password, dbname)
    client.switch_user(user, password)

    print("Drop database: " + dbname)
    client.drop_database(dbname)
    print("Create database: " + dbname)
    client.create_database(dbname)
    
    print ("Sending data to InfluxDB. Please wait...\n")

    client.write_points(json_data, time_precision='ms')
    print("Querying data: " + query)
    result = client.query(query)
    print("Result: {}".format(result))
    print("Total Records inserted in InfluxDB: {} ".format(counter))
