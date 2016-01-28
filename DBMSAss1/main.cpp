//
//  main.cpp
//  DBMSAss1
//
//  Created by Robin Malhotra on 28/01/16.
//  Copyright © 2016 Robin Malhotra. All rights reserved.
//

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <map>
#include <stdio.h>
#include <stdlib.h>
int noOfTables = 0;
using namespace std;
struct schema
{
    string tableName;
    map<string,pair<string, bool>>;// schema["key"].1 = type,schema["key"].1 = isKey
};

struct record
{
    map<string,float> floatValues;
    map<string,string> stringValues;
};
map<string,schema> DB_Schemas;
map<string,record> DB_Records;

void importData()
{
    std::string line;
    std::fstream myfile ("/Users/robinmalhotra/Developer/DBMSAss1/DBMSAss1/input.txt");
    if (myfile.is_open())
    {
        int numberOfTables;
        myfile >> numberOfTables;
        cout<<numberOfTables;
        for (int i=0; i<numberOfTables; i++)
        {
            schema newSchema;
            
            //get tableName
            string tableName;
            myfile >> tableName;
            newSchema.tableName = tableName;
//            DB_Schemas[tableName] = newSchema;
            
            //get the no of attributes
            int noOfAttrs;
            myfile >> noOfAttrs;
            for (int j=0 ; j<noOfAttrs; j++)
            {
                string line;
                getline(myfile, line);
                char attrName[20],attrType[20];
                int attrKey;
                sscanf( line.c_str(), "(%s,%s,%d)", &attrName, &attrType, &attrKey );
                cout<<attrName;
                cout<<attrType;
                cout<<attrKey;
            }
        }
    }
}
int main(int argc, const char * argv[])
{
    // insert code here...
    importData();
    return 0;
}
