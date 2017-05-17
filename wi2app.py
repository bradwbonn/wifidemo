#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Wi2 web app demo

# Known limitations: only supports hardcoded database at present
# Only displays LineString, Polygon, and Point features on map
# Pre-selected locations only
# FACK --- Static Maps will not work... the geoJSON limit is way too small (4096 chars)

import json, requests, os, geojson
from time import time
from flask import Flask, render_template, request, send_from_directory, url_for
from mapbox import Static

app = Flask(__name__, static_url_path='')

@app.route("/", methods=['GET'])
def map():
    return render_template('mapform.html',image='images/japan.png',time='N/A',uri='N/A',message='Ready!')
    
@app.route("/", methods=['POST'])
def search():
    ver("POST received")
    ver(request.form)
    
    newImageName = "images/querymap_{0}.png".format(int(time()))
    
    def get_point(location):
        ver("Setting point")
        if location == "haneda":
            return [139.78111267089844, 35.55436500410275]
        elif location == "greatbuddha":
            return [139.535700, 35.316698]
        elif location == "wi2":
            return [139.769246, 35.673325]
        elif location == "custom":
            return []
        return 
    
    def render_map(formdata):
        ver("Preparing map for: {0}".format(formdata['querylocation']))
        authSelector = dict(
            fencemaster = ("tinetiffeencesidetteryto","1d181a41ebbe621ad2cf7fd5780261efeae17c7e"),
            testfences = ("ieuredislonlyeacticullea","e346439405bc87a5ea7adb3941f5f92bcf83a3c2"),
            pullpaths = ("itsederesedowtherandstra","24c8cb6b93ba3e82a4a07d2e7fb180be29a880b1")
        )
        account = 'bradwbonn'
        db = formdata['database']
        ddoc = 'geoIdx'
        index = 'newGeoIndex'
        myAuth = authSelector[db] # APIキーは読み取り専用です
        
        myPoint = get_point(formdata['querylocation'])
        pointWKT = "point({0}+{1})".format(myPoint[0],myPoint[1]) # longitude first
        
        queryBase = "https://{0}.cloudant.com/{1}/_design/{2}/_geo/{3}?".format(account,db,ddoc,index)
        
        if formdata['querytype'] == "contains":
            queryString = queryBase + "g={0}&limit={1}&relation=contains".format(pointWKT,formdata['limit'])
        elif formdata['querytype'] == "intersects":
            queryString = queryBase + "g={0}&limit={1}&relation=intersects".format(pointWKT,formdata['limit'])
        elif formdata['querytype'] == "nearest":
            queryString = queryBase + "g={0}&limit={1}&nearest=true".format(pointWKT,formdata['limit'])
        elif formdata['querytype'] == "radius":
            queryString = queryBase + "lat={0}&lon={1}&radius={2}&limit={3}".format(
                myPoint[1],
                myPoint[0],
                formdata['radius'],
                formdata['limit']
            )
        
        # first element of returned array is status element.
        # -1 = Cloudant database error
        # 0 = No geo entities found. Show only map with point
        # else: query time for matching geo entities
        
        fences = getFences(queryString,myAuth)
        
        if fences[0] == -1:
            return {
                'queryTime': 0,
                'message': "DATABASE ERROR",
                'uri': queryString
                }
        else:
            featureCollection = buildFeatureCollection(fences, myPoint)
            queryTime = fences[0]
        
        try:
            service = Static()
            # service.session.params['access_token'] = os.environ['MAPBOX_ACCESS_TOKEN']
            #ver("Feature Collection size: {0}".format(len(featureCollection)))
            service.session.params['access_token'] = 'pk.eyJ1IjoiYnJhZHdib25uIiwiYSI6ImNqMjd3bmEwbjAwMjQyeHF0OGp3dm5ibWUifQ.uNds-BFopyeVQY7beRAeQw'
            response = service.image('mapbox.streets', features=featureCollection)
            if response.status_code <> 200:
                ver("Mapbox error: HTTP {0}: {1}".format(response.status_code,response.text))
        except Exception as e:
            ver("Unable to render map: {0}".format(e))
            return {
                'queryTime': 0,
                'message': "Results too large for static map render",
                'uri': queryString
            }            
        
        try:
            with open(newImageName, 'wb') as output:
                output.write(response.content)
            ver("Map image written")
        except Exception as e:
            ver("Cannot write file: {0}".format(e))
            return {
                'queryTime': 0,
                'message': "***Unable to render map!***",
                'uri': queryString
            }
        fencesFound = len(fences) - 1
        if fencesFound > 0:
            message = "Showing {0} matching entities".format(fencesFound)
        else:
            message = "No matching entities"
        return {
            'queryTime': queryTime,
            'message': message,
            'uri': queryString
        }

    
    def buildFeatureCollection(fences, queryPoint):
        ver("Assembling feature collection")
        tempArray = [
            geojson.Feature(
                geometry=geojson.Point(
                    queryPoint
                ),
                properties={'id': "Device Location", 'marker-symbol': 'star', 'marker-color': '#f44'}
            )
        ]
        if fences[0] == 0:
            # send back just the query coordinates as a point
            return geojson.FeatureCollection(tempArray)
        
        else:
            for fence in fences:
                # skip first entry
                if fence == fences[0]:
                    continue
                # Append row's GeoJSON fields to FeatureCollection array
                featureType = fence['geometry']['type']
                if featureType == "Polygon":
                    tempArray.append(
                        geojson.Feature(
                            geometry=geojson.Polygon(
                                fence['geometry']['coordinates']
                            ),
                            properties={'ID': fence['id'],  'color': '0000FF'}
                        )
                    )
                elif featureType == "Point":
                    tempArray.append(
                        geojson.Feature(
                            geometry=geojson.Point(
                                fence['geometry']['coordinates']
                            ),
                            properties={'ID': fence['id'], 'marker-color':'0000FF' }
                        )
                    )
                elif featureType == "LineString":
                    tempArray.append(
                        geojson.Feature(
                            geometry=geojson.LineString(
                                fence['geometry']['coordinates']
                            ),
                            properties={'ID': fence['id'], 'color':'0000FF' }
                        )
                    )
        return geojson.FeatureCollection(tempArray)
    
    def getFences(query,myAuth):
        ver("Querying Cloudant geo database")
        startTime = time()
        try:
            r = requests.get(
                query,
                headers = {'Content-Type': 'application/json'},
                auth = myAuth
            )
        except Exception as e:
            ver("Unable to query Cloudant database: {0}".format(e))
        endTime = time()
        queryTime = round((endTime - startTime),2)
        if r.status_code != 200:
            return [-1]
        jsonResponse = r.json()
        if len(jsonResponse['rows']) == 0:
            return [0]
        fenceIDs = [queryTime]
        for row in jsonResponse['rows']:
            fenceIDs.append(row)
        ver("Query complete in {0} sec, items found: {1}".format(queryTime,len(jsonResponse['rows'])))
        return fenceIDs
    
    mapMetaData = render_map(request.form)
    if mapMetaData['message'] == "No matching entities":
        returnImage = 'images/japan.png'
    elif mapMetaData['message'] == "***Unable to render map!***":
        returnImage = 'images/japan.png'
    elif mapMetaData['message'] == "Results too large for static map render":
        returnImage = 'images/japan.png'
    else:
        returnImage = newImageName
    return render_template(
        'mapform.html',
        image=returnImage,
        time=mapMetaData['queryTime'],
        message=mapMetaData['message'],
        uri=mapMetaData['uri']
    )
    
#@app.route("/")
#def show_japan():
#    service = Static()
#    service.session.params['access_token'] = os.environ['MAPBOX_ACCESS_TOKEN']
#    response = service.image('mapbox.streets',
#        lon=139.769246,
#        lat=35.673325,
#        z=12)
#    with open('images/japan.png', 'wb') as output:
#        output.write(response.content)
#    return render_template('mapform.html',image='japan.png')

# Print function for verpose diagnostics
def ver(printThis):
    print " {0}".format(printThis)

@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('images', path)

#@app.route('/tmp/<path:path>')
#def send_tmp(path):
#    return send_from_directory('tmp', path)


if __name__ == "__main__":
    app.run(debug=True)