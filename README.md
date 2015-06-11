# wifidemo
Scripts for wifi geo tracking example
### fenceparser.py:
Loads data about geofence radii from raw file out of S3
### locationparser.py:
Loads data about daily activty from raw file out of S3.  Includes a parsing of the data string to extract location and identifying data points.
### pointstopaths.py:
Script to take check-in point locations by each device ID, and convert them into linestring features in the wifipaths database
### wifidemo:
Database that holds the user activity log data points
### wifipaths:
Database that holds the determined paths from source data in "wifidemo"
### testfences:
Database that holds the partner "fence" radii.

## TO-DO:
* Create near-circluar polygons of the geofence points for polling of intersecting paths
* Update pointstopaths.py to only create path objects which correspond to continous travel motion.  Single-point paths then get left alone as merely points.

