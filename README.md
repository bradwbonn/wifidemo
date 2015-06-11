# wifidemo
Scripts for wifi geo tracking example
### fenceparser.py:
Loads data about geofence radii from raw file out of S3
### locationparser.py:
Loads data about daily activty from raw file out of S3.  Includes a parsing of the data string to extract location and identifying data points.
### pointstopaths.py:
Script to take check-in point locations by each device ID, and convert them into linestring features in the wifipaths database
### mapdemo.html
Web page for the demo couchapp which will display an interactive map, showing results for various users
### wifidemo:
Database that holds the user activity log data points
### wifipaths:
Database that holds the determined paths from source data in "wifidemo"
### testfences
Database that holds the partner "fence" radii.



