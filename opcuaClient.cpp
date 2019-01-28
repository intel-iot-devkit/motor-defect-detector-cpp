/*
* Copyright (c) 2018 Intel Corporation.
*
* Permission is hereby granted, free of charge, to any person obtaining
* a copy of this software and associated documentation files (the
* "Software"), to deal in the Software without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Software, and to
* permit persons to whom the Software is furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be
* included in all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
* NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
* LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
* OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
* WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

/**
 * OPC-UA Client 
 * --------------------------
 * This code will receive the NASA bearing data sent from the OPC-UA server
 * and stores the received data to InfluxDB. If the server
 * is shut down while the client is connected, client tries to connect 
 * for 5 seconds and then it disconnects automatically.
 */

#include <fstream>
#include <iostream>
#include <signal.h>
#include <open62541.h>

/* macro definition to distinguish between 1st and 2nd dataset */
#define arraySize 20000
using namespace std;

UA_Boolean running = true;


/*
* Signal handling function. Terminates any function 
* on receiving ctrl-c
*
* @param sign: receives signal
* @return none
*/
void signalHandler(int sig) 
{
    UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_SERVER, "received ctrl-c");
    running = false;
}


/*
* Read the node values sent by the server. Value received 
* from server is either a single value or it an be array.  
* In this case array of float type is received.
*
* @param none
* @return status
*/
int main(int argc, char *argv[])
{
    /* Create a client and connect to server */
    UA_Client *client = UA_Client_new(UA_ClientConfig_default);
    UA_StatusCode status = UA_Client_connect(client, "opc.tcp://localhost:4840");
    if(status != UA_STATUSCODE_GOOD) 
    {
        UA_Client_delete(client);
        return status;
    }

    /* Read the value attribute of the node. UA_Client_readValueAttribute is a
     * wrapper for the raw read service available as UA_Client_Service_read. */

    /* Variants can hold scalar values and arrays of any type */
    UA_Variant value;
    UA_Variant_init(&value);
    status = UA_Client_readValueAttribute(client, UA_NODEID_STRING(1, "bearingNode"), &value);

    if(status == UA_STATUSCODE_GOOD && UA_Variant_hasArrayType(&value, &UA_TYPES[UA_TYPES_FLOAT])) 
    {
        UA_Float *ns = (UA_Float*)value.data;
        int count;
        int noOfColumn;
        int retVal;

        /* Catch ctrl-c */
        signal(SIGINT, signalHandler); 

        noOfColumn = ((value.arrayLength > arraySize) ? 8 : 4);

        ofstream bearingFile;
        bearingFile.open("bearingDataFile");
        count = 0;
        if(bearingFile.is_open())
        {
            for(size_t i = 0; i < value.arrayLength; ++i)
            {
                bearingFile << ns[i] << "\t" ;
                count ++;
                if(count == noOfColumn)
                {
                    bearingFile << "\n";
                    count = 0;
                } 
            }
            UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_CLIENT, "Data received from OPC-UA Server");
        }
        else
        {
            UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_CLIENT, "Unable to open file");
            /* Clean up */
            UA_Variant_deleteMembers(&value);
            /* Disconnects the client internally */
            UA_Client_delete(client);  
            exit(0);
        }
        
        bearingFile.close();
        retVal = system("./influxScript.sh bearingDataFile");

        /* Clean up */
        UA_Variant_deleteMembers(&value);
        /* Disconnects the client internally */
        UA_Client_delete(client); 

        if(retVal != 0)
        {
            UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_CLIENT, "Error while calling the python script");
            exit(0);
        }
        UA_LOG_INFO(UA_Log_Stdout, UA_LOGCATEGORY_CLIENT, "Successfully inserted data to InfluxDB");
        remove( "bearingDataFile");
    }
    return status;
}
