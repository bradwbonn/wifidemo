#!/usr/bin/env python

import json
import requests
import sys, os
import re
from pprint import pprint
from geojson import Feature, Point
import cloudant

insert_batch_size = 2000
inputfile = 'location-log.json'
username = os.environ['CLOUDANTUSER']
password = os.environ['CLOUDANTPASS']
db_name = os.environ['DEMODB']
baseUri = "https://{0}.cloudant.com/{1}".format(username, db_name)
bulkUri = "{0}/_bulk_docs".format(baseUri)
creds = (username, password)

#account = cloudant.Account(username)
#future = account.login(username,password)
#db = account.database(db_name)

doc_insert_list = []

with open(inputfile) as data_file:    
    data = json.load(data_file)
    
counter = 1
errors = 0

def point_insert(jsondoc):
    response = requests.post(
        baseUri,
        data=json.dumps(jsondoc),
        auth=creds,
        headers={"Content-Type": "application/json"}
    )
    
def bulk_insert(doclist):
    print "Inserting {0} docs, {1} total documents so far...".format(len(doclist),counter)
    #response = db.bulk_docs(str(doclist).strip('[]'))
    #formatteddoclist = '{ "docs": '+str(doclist)+' }'
    formatteddoclist = json.dumps({"docs":doclist})
    
    response = requests.post(
        bulkUri,
        data=formatteddoclist,
        auth=creds,
        headers={"Content-Type": "application/json"}
    )
    #print response.status_code
    #print formatteddoclist
        
for inputdoc in data:
    parseline = inputdoc["data"]
    found = re.search('(.+)\\t(.+)\\t(.+)\\t([-]*?[0-9]+[,.][0-9]+)\,([-]*?[0-9]+[,.][0-9]+)\\t(.+)', parseline)
    if found:
        userArg1 = found.group(1)
        userArg2 = found.group(2)
        userArg3 = found.group(3)
        p = re.compile(',')
        latitude = p.sub( '.', found.group(4))
        latitude = float(latitude)
        longitude = p.sub( '.', found.group(5))
        longitude = float(longitude)
        timestamp = found.group(6)
        my_point = Point((longitude,latitude))
        my_feature = Feature(geometry=my_point, properties={"userID": userArg1, "arg2": userArg2, "arg3": userArg3, "date": timestamp})
        doc_insert_list.append(my_feature)
        if int(counter) / int(insert_batch_size) == int(counter) / float(insert_batch_size):
            bulk_insert(doc_insert_list)
            doc_insert_list = []
        counter = counter + 1
    else:
        print "Skipping invalid record..."
        pprint(parseline)
        errors = errors + 1
        continue
# Add final batch
if len(doc_insert_list) > 0:
    bulk_insert(doc_insert_list)
    
print "COMPLETE: Malformed entries: {0}".format(errors)

