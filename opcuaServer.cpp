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
 * OPC-UA Server
 * --------------------------
 * This code will read the NASA bearing data set from file given 
 * in command line argument by the user and send the bearing 
 * data to OPC-UA client.
 */

#include <fstream>
#include <iostream>
#include <signal.h>
#include <sstream>
#include <vector>
#include <open62541.h>

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
* Reads the file given in the argument, and returns
* the vector containing the elements of the csv file
*
* @param fileName: file to read
* @return fileVector: elements in the file
*/
vector<UA_Float> readFile(string fileName)
{
    int noOfTokens;
    int noOfBearings;
    ifstream file;
    string line;
    vector<UA_Float> fileVector;
    file.open(fileName.c_str());
    noOfTokens = ((strcmp(fileName.c_str(), "1st_test.csv")==0) ? 8 : 4);
    if((file.is_open()) && !(file.peek() == std::ifstream::traits_type::eof()))
    {
        while (getline(file, line)) 
        {
            stringstream ss(line);
            string token[noOfTokens];
            noOfBearings = 0;
            while(getline(ss,token[noOfBearings],','))
            {
                fileVector.push_back(atof(token[noOfBearings].c_str()));
                noOfBearings++;
            }
        }
    }
    else
    {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_SERVER, "Unable to open file or, the file is empty.");
        exit(0);
    }
    return fileVector;
}


/*
* This function writes the given file data to node  
* in array format and then publishes it to OPC-UA Client
*
* @param command line arguments: 1st_test or 2nd_test
* @return: status 
*/
int main(int argc, char** argv)
{
    if (argc != 2)
    {
        cout << "Usage: " << endl;
        cout << "./opcuaServer 1st_test.csv or," << endl;
        cout << "./opcuaServer 2nd_test.csv" << endl;
    }
    else if ((argc == 2) && (strcmp(argv[1], "1st_test.csv")==0 || strcmp(argv[1], "2nd_test.csv")==0))
    {
        int tokenCount;
        int size;
        vector<UA_Float> fileElementVector;

        /* catch ctrl-c */
        signal(SIGINT, signalHandler); 

        /* Create a server listening on port 4840 */
        UA_ServerConfig *config = UA_ServerConfig_new_default();
        UA_Server *server = UA_Server_new(config);

        /* Defining the node attributes */
        UA_VariableAttributes attr = UA_VariableAttributes_default;
        attr.displayName = UA_LOCALIZEDTEXT("en-US", "bearingNode");
        
        /* Calling the readFile function and storing the return value in vector */
        fileElementVector = readFile(argv[1]);
        size = fileElementVector.size();
        
        UA_Float arr[size];
        copy(fileElementVector.begin(), fileElementVector.end(), arr);
        UA_Variant_setArrayCopy(&attr.value, &arr, size, & UA_TYPES[UA_TYPES_FLOAT]);

        /* Defining where the node shall be added and defining the browsename */
        UA_NodeId newNodeId = UA_NODEID_STRING(1, "bearingNode");
        UA_NodeId parentNodeId = UA_NODEID_NUMERIC(0, UA_NS0ID_OBJECTSFOLDER);
        UA_NodeId parentReferenceNodeId = UA_NODEID_NUMERIC(0, UA_NS0ID_ORGANIZES);
        UA_NodeId variableType = UA_NODEID_NULL; /* take the default variable type */
        UA_QualifiedName browseName = UA_QUALIFIEDNAME(1, "bearingNode");

        /* Adding node */
        UA_Server_addVariableNode(server, newNodeId, parentNodeId, parentReferenceNodeId,
                                browseName, variableType, attr, NULL, NULL);

        /* Runing the server loop */
        UA_StatusCode status = UA_Server_run(server, &running);
        UA_Server_delete(server);
        UA_ServerConfig_delete(config);
        return status;
    }
    else
    {
        UA_LOG_ERROR(UA_Log_Stdout, UA_LOGCATEGORY_SERVER, "Enter valid directory name either 1st_test.csv or 2nd_test.csv");
        exit(0);
    }
    return 0;
}
