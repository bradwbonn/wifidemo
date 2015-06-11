#!/usr/bin/env python

import json
import requests
import sys, os
import re
from pprint import pprint
from geojson import Feature, Point
import cloudant

insert_batch_size = 1000
inputfile = 'geofence.json'
username = os.environ['CLOUDANTUSER']
password = os.environ['CLOUDANTPASS']
db_name = 'testfences'
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
    fenceID = inputdoc["fenceId"]
    latitude = float(inputdoc["range"][0]["circleLat"])
    longitude = float(inputdoc["range"][0]["circleLng"])
    radius = float(inputdoc["range"][0]["circleRad"])*1000
    my_point = Point((longitude,latitude))
    my_feature = Feature(geometry=my_point, properties={"radius": radius}, _id=fenceID)
    doc_insert_list.append(my_feature)
    if int(counter) / int(insert_batch_size) == int(counter) / float(insert_batch_size):
        bulk_insert(doc_insert_list)
        doc_insert_list = []
    counter = counter + 1
# Add final batch
if len(doc_insert_list) > 0:
    bulk_insert(doc_insert_list)
    
print "COMPLETE: Malformed entries: {0}".format(errors)
