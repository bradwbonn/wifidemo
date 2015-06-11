#!/usr/bin/env python

import json
from geojson import LineString
from geojson import Point
from geojson import Feature
import os
import requests
import pprint
import sys
import datetime

demoqueryURI = "https://bradwbonn.cloudant.com/wifidemo/_design/users/_view/usertrack?include_docs=true&startkey=%5B%220005cf9d54f3ebc0ef4881e2f96eca57%22%2C%22%22%5D&endkey=%5B%220005cf9d54f3ebc0ef4881e2f96eca57%22%2C%222015-05-28T23%3A59%3A59%2B07%3A00%22%5D&inclusive_end=true"

username = os.environ["CLOUDANTUSER"]
password = os.environ["CLOUDANTPASS"]
creds = (username, password)
sourcedbname = "wifidemo"
pathsdbname = "wifipaths"
insert_batch_size = 100
counter = 1
doc_insert_list = []

viewURI = "https://{0}.cloudant.com/{1}/_design/users/_view/usertrack".format(username,sourcedbname)
viewqueryprefix = "?include_docs=true&inclusive_end=false&reduce=false"
devicequeryURI = viewURI+"?group_level=1&reduce=true"
bulkUri = "https://{0}.cloudant.com/{1}/_bulk_docs".format(username,pathsdbname)

deviceIDs = requests.get(
    devicequeryURI,
    auth=creds,
    headers={"Content-Type": "application/json"}
)
print "List of ID's collected. Total count: {0}".format(len(deviceIDs.json()["rows"]))
#for testid in deviceIDs.json()["rows"]:
#    print testid

#https://bradwbonn.cloudant.com/wifidemo/_design/users/_view/usertrack?include_docs=true&startkey=%5B%22id%22%2C%22%22%5D&endkey=%5B%22id%22%2C%7B%7D%5D&inclusive_end=false
def bulk_insert(doclist):
    formatteddoclist = json.dumps({"docs":doclist})
    response = requests.post(
        bulkUri,
        data=formatteddoclist,
        auth=creds,
        headers={"Content-Type": "application/json"}
    )
    print "Bulk insert triggered: {0}".format(response.status_code)

def getpathpoints(devID):
    pointset = []
    #https://bradwbonn.cloudant.com/wifidemo/_design/users/_view/usertrack?include_docs=true&startkey=%5B%22000262b3d75c45e3f6c5939d717fca4a%22%2C%22%22%5D&endkey=%5B%22000262b3d75c45e3f6c5939d717fca4a%22%2C%7B%7D%5D&inclusive_end=false
    URI = viewURI+viewqueryprefix+"&startkey=%5B%22"+devID+"%22%2C%22%22%5D&endkey=%5B%22"+devID+"%22%2C%7B%7D%5D"
    response = requests.get(
        URI,
        auth=creds,
        headers={"Content-Type": "application/json"}
    )
    for point in response.json()["rows"]:
        coordinates = point["doc"]["geometry"]["coordinates"]
        pointset.append(coordinates)
    return pointset
    #print pointset
    
# Convert each device's check-in points to a path and insert it into the target database
for deviceid in deviceIDs.json()["rows"]:
    thisdeviceid = deviceid["key"][0]
    #print "Gathering points for ID: {0} ({1})".format(thisdeviceid,counter)
    datapoints = getpathpoints(thisdeviceid)
    newpath = LineString(datapoints)
    todaysdate = str(datetime.date.today())
    my_feature = Feature(geometry=newpath, properties={"dateadded": todaysdate}, _id=deviceid["key"][0])
    doc_insert_list.append(my_feature)
    sys.stdout.write(".")
    sys.stdout.flush()
    if int(counter) / int(insert_batch_size) == int(counter) / float(insert_batch_size):
        bulk_insert(doc_insert_list)
        doc_insert_list = []
    counter = counter + 1
# Insert any remaining rows into database
if len(doc_insert_list) > 0:
    bulk_insert(doc_insert_list)
