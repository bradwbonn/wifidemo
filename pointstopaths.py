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
import re

demoqueryURI = "https://bradwbonn.cloudant.com/wifidemo/_design/users/_view/usertrack?include_docs=true&startkey=%5B%220005cf9d54f3ebc0ef4881e2f96eca57%22%2C%22%22%5D&endkey=%5B%220005cf9d54f3ebc0ef4881e2f96eca57%22%2C%222015-05-28T23%3A59%3A59%2B07%3A00%22%5D&inclusive_end=true"

username = os.environ["CLOUDANTUSER"]
password = os.environ["CLOUDANTPASS"]
creds = (username, password)
sourcedbname = "wifidemo"
pathsdbname = "wifipaths"
insert_batch_size = 500
counter = 1
#doc_insert_list = []
# Number of seconds before a new path is started for a device
pathtimeout = (60 * 5)

viewURI = "https://{0}.cloudant.com/{1}/_design/users/_view/usertrack".format(username,sourcedbname)
viewqueryprefix = "?include_docs=true&inclusive_end=false&reduce=false"
devicequeryURI = viewURI+"?group_level=1&reduce=true"
bulkUri = "https://{0}.cloudant.com/{1}/_bulk_docs".format(username,pathsdbname)

#https://bradwbonn.cloudant.com/wifidemo/_design/users/_view/usertrack?include_docs=true&startkey=%5B%22id%22%2C%22%22%5D&endkey=%5B%22id%22%2C%7B%7D%5D&inclusive_end=false
def bulk_insert(doclist):
    formatteddoclist = json.dumps({"docs":doclist})
    response = requests.post(
        bulkUri,
        data=formatteddoclist,
        auth=creds,
        headers={"Content-Type": "application/json"}
    )
    print "Bulk insert triggered - HTTP Code: {0}".format(response.status_code)

def gettimedifference(current, last):
    d = current - last
    return d.seconds

def getpathpoints(devID):
    pointset = []
    doc_insert_list = []
    # Get all GPS points for the device
    URI = viewURI+viewqueryprefix+"&startkey=%5B%22"+devID+"%22%2C%22%22%5D&endkey=%5B%22"+devID+"%22%2C%7B%7D%5D"
    response = requests.get(
        URI,
        auth=creds,
        headers={"Content-Type": "application/json"}
    )
    # Loop through all resulting points
    for point in response.json()["rows"]:
        # Obtain current point coordinates
        coordinates = point["doc"]["geometry"]["coordinates"]
        # Get timestamp for this point and store as datetime object
        timestamp = point["doc"]["properties"]["date"]
        found = re.search('^([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})', timestamp)
        pointyear = int(found.group(1))
        pointmonth = int(found.group(2))
        pointday = int(found.group(3))
        pointhour = int(found.group(4))
        pointminute = int(found.group(5))
        pointsecond = int(found.group(6))
        thistime = datetime.datetime(pointyear,pointmonth,pointday,pointhour,pointminute,pointsecond)
        # If we are the first point, append, store timestamp, and continue to the next one.
        if (len(pointset) == 0):
            pointset.append(coordinates)
            lasttime = thistime
            firsttime = thistime
        # If we are not the first point, and time difference is < the fixed gap, append this point and continue
        elif ((len(pointset) > 0) and (gettimedifference(thistime, lasttime) <= pathtimeout)):
            pointset.append(coordinates)
            lasttime = thistime
        # If we are not the first point, but time difference is > the fixed gap, and len(pointset) > 1, store pointset as path, then reset pointset
        elif ((len(pointset) > 1) and (gettimedifference(thistime, lasttime) > pathtimeout)):
            newpath = LineString(pointset)
            my_feature = Feature(geometry=newpath, properties={"stoptime": thistime.isoformat(), "starttime": firsttime.isoformat()})
            doc_insert_list.append(my_feature)
            pointset = []
            # Insert when batch counted
            if len(doc_insert_list) / int(insert_batch_size) == len(doc_insert_list) / float(insert_batch_size):
                bulk_insert(doc_insert_list)
                doc_insert_list = []
            sys.stdout.write(".")
            sys.stdout.flush()
        # If we are not the first point, but time difference is > the fixed gap, and len(pointset) = 1, don't store, reset pointset and continue
        elif ((len(pointset) == 1) and (gettimedifference(thistime, lasttime) > pathtimeout)):
            pointset = []
    # Insert any remaining rows into database once loop through all rows is complete
    if len(doc_insert_list) > 0:
        bulk_insert(doc_insert_list)
        doc_insert_list = []

# Get full list of device IDs from database view
deviceIDs = requests.get(
    devicequeryURI,
    auth=creds,
    headers={"Content-Type": "application/json"}
)
print "List of ID's collected. Total count: {0}".format(len(deviceIDs.json()["rows"]))
    
# Convert each device's check-in points to a path and insert it into the target database
for deviceid in deviceIDs.json()["rows"]:
    thisdeviceid = deviceid["key"][0]
    getpathpoints(thisdeviceid)
