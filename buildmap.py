#!/usr/bin/env python
import sys, os, json, requests
from geojson import FeatureCollection, Feature, Point

inputfile = "~/src/wifidata/Shibuya.wkt"
baseuri = 'https://bradwbonn.cloudant.com/'

username = os.environ['CLOUDANTUSER']
password = os.environ['CLOUDANTPASS']
creds = (username, password)

fencedb = 'testfences'
locationdb = 'wifidemo'
targetdb = 'wifimapdemo'

# Query database for all partner fence centers inside Shibuya using geo index
def getFencesInRegion(wktfeature):
    # Set query parameters
    index = "/_design/geodd/_geo/geoidx"
    arg1 = "&include_docs=true"
    arg2 = "&limit=200"
    arg3 = "&relation=contains"
    arg4 = "&format=geojson"
    geometry = "?g="+wktfeature
    jsonheader = {"Content-Type": "application/json"}
    # Query the geo index with the region as the polygon contains query
    URI = baseuri+fencedb+index+geometry+arg1+arg2+arg3+arg4
    response = requests.get(
        URI,
        auth=creds,
        headers=jsonheader
    )
    return response.json()

# Execute radius query for check-in location and return total count
def getCheckinsForFence(fencecoordinates, fenceradius):
    # Set query parameters
    index = "/_design/geodd/_geo/geoidx"
    arg1 = "&lat="+str(fencecoordinates[1])
    arg2 = "&lon="+str(fencecoordinates[0])
    arg3 = "&relation=contains"
    geometry = "?radius="+str(fenceradius)
    jsonheader = {"Content-Type": "application/json"}
    # Query the geo index for all location check-ins in a radius from the current point
    URI = baseuri+locationdb+index+geometry+arg1+arg2+arg3
    response = requests.get(
        URI,
        auth=creds,
        headers=jsonheader
    )
    # Return the total count of matching locations, up to the maximum 200
    # This is the maximum limit of responses per geo query.  More than this requires bookmark parsing, which can be done later for more
    # detailed counts.  In this demo we're just showing a relative count.
    rows = len(response.json()["rows"])
    return rows
    
# Insert results into GeoJSON-formatted documents with Google Maps API coded properties to show colors corresponding to frequency values
def putMapObjects(collection):
    formatteddoclist = json.dumps({"docs":collection})
    bulkUri = baseuri+targetdb+"/_bulk_docs"
    try:
        response = requests.post(
            bulkUri,
            data=formatteddoclist,
            auth=creds,
            headers={"Content-Type": "application/json"}
        )
    except requests.exceptions.RequestException as e:
        print e
        sys.exit()
    except requests.exceptions.ConnectionError:
        print "Connection refused. Re-trying after 15s sleep"
        sleep(15)
        try:
            response = requests.post(
            bulkUri,
            data=formatteddoclist,
            auth=creds,
            headers={"Content-Type": "application/json"}
        )
        except requests.exceptions.ConnectionError:
            print "Retry failed. Giving up."
            sys.exit()
    
# Get a color value for the given numberical range
def getColor(count):
    if (count == 0):
        color = "FFFFFF"
    elif (count <= 2 and count > 0):
        color = "E6EBFA"
    elif (count <= 5 and count > 2):
        color = "CCD6F5"
    elif (count <= 8 and count > 5):
        color = "B2C2F0"
    elif (count <= 11 and count > 8):
        color = "99ADEB"
    elif (count <= 14 and count > 11):
        color = "8099E6"
    elif (count <= 18 and count > 14):
        color = "6685E0"
    elif (count <= 21 and count > 18):
        color = "4D70DB"
    elif (count <= 24 and count > 21):
        color = "335CD6"
    elif (count > 24):
        color = "1947D1"
    color = "#"+color
    return color

# Main section here

# Load the feature in WKT format as a string
#with open(inputfile) as data_file:
#    regionwkt = data_file
regionwkt = "POLYGON ((139.686628 35.682609, 139.68747475000006 35.681752, 139.68861 35.68219462500008, 139.690876 35.683812, 139.694459 35.686288, 139.69529025000008 35.68677875000009, 139.6962215000001 35.687174, 139.70045975000005 35.68884450000007, 139.70138 35.689041, 139.702099 35.689169, 139.70578 35.688048, 139.7147919370001 35.680676334000054, 139.71438250000003 35.67992012500008, 139.7135575000001 35.67846350000007, 139.712898 35.677166, 139.712891 35.674618, 139.7169471850001 35.67364177400009, 139.71135992000006 35.66693111100005, 139.7106670510001 35.66621156400004, 139.70861450000007 35.66418625000006, 139.713196 35.658281, 139.714693 35.65724650000004, 139.71806475000005 35.65672912500008, 139.721971 35.655603, 139.723557 35.646701, 139.722711001 35.64471750000007, 139.7216455 35.64440575000009, 139.71903405700004 35.641765553000084, 139.71762211300006 35.641645947000086, 139.710104 35.641574, 139.709386 35.641746, 139.708621 35.642007, 139.707528 35.642694, 139.704748 35.644587, 139.695888 35.650682, 139.69321 35.653658, 139.691649 35.655874, 139.690045 35.658077, 139.68711075000007 35.66172812500008, 139.685143 35.66263150000009, 139.684141 35.662909, 139.67957025000007 35.66381750000005, 139.678107 35.663939, 139.67717091600002 35.66390953300004, 139.6764509840001 35.66386154600008, 139.6754908810001 35.66382317700004, 139.6747333620001 35.663914152000075, 139.67424833300004 35.66449516700004, 139.67322150000007 35.66643650000009, 139.6728283330001 35.667396, 139.669917 35.671778, 139.663101 35.671485, 139.6618547500001 35.67172212500009, 139.66155267200008 35.672395546000075, 139.66211650000002 35.673545501000035, 139.661815992 35.67439460800006, 139.66222807100007 35.67562285900004, 139.66315266700008 35.676004, 139.66418750600008 35.67646178300003, 139.66483950000008 35.676667001000055, 139.6655495 35.67717983300008, 139.666104 35.67804875100006, 139.666556507 35.67886060300009, 139.66712405700002 35.67937305600009, 139.66771745300002 35.67985707200006, 139.669012 35.680608, 139.670081 35.681078, 139.671372 35.681554, 139.67515 35.684661, 139.67569450000008 35.685623, 139.676785 35.686667, 139.67779775000008 35.68735312500007, 139.6793120330001 35.68858568300004, 139.68015539600003 35.68955106200008, 139.68103642100002 35.69023692600007, 139.68316581300007 35.691677162000076, 139.683987 35.692172, 139.683292206 35.68912331800004, 139.685809 35.683575, 139.686628 35.682609))"
    
# Obtain a geo feature collection of all fence locations in the selected region
fences = getFencesInRegion(regionwkt)

# Get the count of checkins and corresponding highlight color for each, and insert a new doc
# into the array of documents that highlights each location
fencescrossed = []
for thisfence in fences["features"]:
    pointcoordinates = thisfence["geometry"]["coordinates"]
    #pointcount = getCheckinsForFence(pointcoordinates, thisfence["properties"]["radius"])
    pointcount = getCheckinsForFence(pointcoordinates, 100)
    pointcolor = getColor(pointcount)
    pointid = thisfence["_id"]
    pointproperties = {"fenceID":pointid,"marker-color": pointcolor, "marker-symbol":"triangle", "marker-size": "medium", "count":pointcount}
    mappoint = Point(pointcoordinates)
    myfeature = Feature(geometry=mappoint, properties=pointproperties, _id=pointid)
    fencescrossed.append(myfeature)

# Write featurecollection to file for now
mapcollection = FeatureCollection(fencescrossed)
outputfile = open("mapcollection.json","w")
json.dump(mapcollection, outputfile)

