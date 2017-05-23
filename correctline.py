#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests, json, geojson, sys, time
from mapbox import MapMatcher

c = dict(
    # Set variables
    destAPIKey = ("wsticallyingencessisenig","fb9fbc35872348954aefff64fe3d99f0a46c2bc4"),
    srcAPIKey = ("diaccarthereselyingensid","1fa4571f5365d6991b036c67713ace151cc9bab9"),
    srcDB = 'spapp',
    destDB = 'wi2demo',
    urlbase = "https://bradwbonn.cloudant.com/",
    mapboxToken = 'pk.eyJ1IjoiYnJhZHdib25uIiwiYSI6ImNqMjd3bmEwbjAwMjQyeHF0OGp3dm5ibWUifQ.uNds-BFopyeVQY7beRAeQw'
)

def main():
    clear_DB()
    deviceID = select_device()
    uncorrectedLine = get_device_points(deviceID)
    rev = insert_raw_line(uncorrectedLine)
    correction(uncorrectedLine, rev)

# Delete passed docID and rev
def delete_doc(docID, rev):
    r = requests.delete(
        url = "{0}{1}/{2}".format(c['urlbase'],c['destDB'],docID),
        params = {
            'rev': rev
        },
        auth = c['destAPIKey']
    )

# Get all doc IDs and revs in DB
def get_all_docs():
    allDocs = []
    r = requests.get(
        url = "{0}{1}/_all_docs".format(c['urlbase'],c['destDB']),
        auth = c['destAPIKey']
    )
    for row in r.json()['rows']:
        allDocs.append([row['id'],row['value']['rev']])
    return allDocs
    
# Remove previous data points
def clear_DB():
    docs = get_all_docs()
    delete_docs = dict(
        docs = []
    )
    for doc in docs:
        docID = doc[0]
        rev = doc[1]
        if "pathafter" in docID or "pathbefore" in docID:
            delete_docs['docs'].append(
                {
                    "_id": docID,
                    "_rev": rev,
                    "_deleted": True
                }
            )
    r = requests.post(
        url = "{0}{1}/_bulk_docs".format(c['urlbase'],c['destDB']),
        data = json.dumps(delete_docs),
        auth = c['destAPIKey'],
        headers = {'Content-Type': 'application/json'}
    )

# Select from available device tracks in spapp
def select_device():
    print "Choose from the following list of possible devices: "
    selector = 1
    devices = []
    for device in get_devices():
        print "{0}: {1} Points: {2}".format(selector,device[0],device[1])
        devices.append(device[0])
        selector = selector + 1
    choice = raw_input(" > ")
    deviceID = devices[int(choice)-1]
    return deviceID

# Get matching device profiles from spapp        
def get_devices():
    r = requests.get(
        url = "{0}{1}/_design/devices/_view/paths".format(c['urlbase'],c['srcDB']),
        params = {
            'limit': 200,
            'reduce': 'true',
            'group_level': 1
        },
        auth = c['srcAPIKey']
    )
    devices = []
    for row in r.json()['rows']:
        if (row['value'] >= 20 and row['value'] <= 100):
            devices.append([row['key'][0],row['value']])
            if len(devices) >= 30:
                return devices
    return devices


def get_device_points(deviceID):
    # Get points for selected device
    try:
        r = requests.get(
            url = "{0}{1}/_design/devices/_view/paths".format(c['urlbase'],c['srcDB']),
            params = {
                'reduce': 'false',
                'start_key': json.dumps([deviceID,0]),
                'end_key': json.dumps([deviceID,{}])
            },
            auth = c['srcAPIKey']
        )
    except Exception as e:
        print e

    if r.status_code <> 200:
        sys.exit("Cloudant: {0}".format(r))
    
    coordTimes=[]
    coordinates=[]
    lastTime = 0
    
    for row in r.json()['rows']:
        if lastTime <> row['key'][1]:
            coordTimes.append(row['key'][1])
            coordinates.append(row['value'])
            lastTime = row['key'][1]
        
    uncorrectedLine = geojson.Feature(
        geometry=geojson.LineString(coordinates),
        properties={
            'deviceID': deviceID,
            'coordTimes': coordTimes
        }
    )
    
    return uncorrectedLine

def insert_raw_line(uncorrectedLine):
    # Insert uncorrected line and wait for user input
    
    r = requests.put(
        url = "{0}{1}/pathbefore".format(c['urlbase'],c['destDB']),
        auth = c['destAPIKey'],
        data = json.dumps(uncorrectedLine)
    )
    waiting = raw_input(" View raw line in map: https://bradwbonn.cloudant.com/dashboard.html#/database/wi2demo/_design/geoIdx/_geoindex/newGeoIndex\nPress Enter after viewing.")
    return r.json()['rev']

def correction(uncorrectedLine, rev):
    # Delete uncorrected line from DB
    delete_doc('pathbefore',rev)
    
    # Pull corrected linestring from Mapbox API
    service = MapMatcher()
    service.session.params['access_token'] = c['mapboxToken']
    
    matchProfiles = [
        'walking',
        'driving',
        'cycling'
    ]
    
    for profile in matchProfiles:
        goodMatches = 0
        try:
            mapboxProfile = "mapbox.{0}".format(profile)
            response = service.match(uncorrectedLine, profile=mapboxProfile, gps_precision=10)
            for correctedLine in response.geojson()['features']:
                print "{0} match confidence: {1}".format(profile,correctedLine['properties']['confidence'])
                if correctedLine['properties']['confidence'] > 0.0001:
                    # Insert new linestring feature into database
                    r = requests.put(
                        url = "https://bradwbonn.cloudant.com/wi2demo/pathafter_{0}_{1}".format(profile,time.time()),
                        auth = c['destAPIKey'],
                        data = json.dumps(correctedLine)
                    )
                    goodMatches = goodMatches + 1
        except Exception as e:
            print "Couldn't match {0}: {1}".format(profile,e)
            
    if goodMatches > 0:
        print "Decent matches found!"
    else:
        print "No good matches found, data probably bad."

if __name__ == "__main__":
    main()