# wifidemo
Scripts for wifi geo tracking example
### fenceparser.py:
Loads data about geofence radii from raw file out of S3
### locationparser.py:
Loads data about daily activty from raw file out of S3.  Includes a parsing of the data string to extract location and identifying data points.
### pointstopaths.py:
Script to take check-in point locations by each device ID, and convert them into linestring features in the wifipaths database
### buildmap.py:
Simple script that uses Cloudan't geo-spatial index to create a color-coded map of Shibuya's partner geofence locations, with darker blue color for fence IDs that have more device check-ins within a 100-meter radius. This simple demo uses geojson.io to create an interactive map representation of the results.

### https://bradwbonn.cloudant.com/wifidemo
Database that holds the user activity log data points
### https://bradwbonn.cloudant.com/wifipaths
Database that holds the determined paths from source data in "wifidemo"
### https://bradwbonn.cloudant.com/testfences
Database that holds the partner "fence" radii.

## Map of partner fences to demo from:
http://bl.ocks.org/d/ef47f8d020bf10e66388

## Completed Map of locations with most frequent device check-ins within 100 meters is shown here:
https://gist.github.com/bradwbonn/a2f96c0de6efa0674d9e

## TO-DO:
* ~~Create near-circluar polygons of the geofence points for polling of intersecting paths~~
* ~~Create query script to obtain the most commonly crossed geofences, displaying geojson on google maps with highlight colors for frequency~~
* Resolve anomalous data points > Must be done at app level and tagged as either IP or GPS-sourced data points in the JSON

