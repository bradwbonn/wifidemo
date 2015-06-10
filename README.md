# wifidemo
Scripts for wifi geo tracking example
### fenceparser.py:
Loads data about geofence radii from raw file out of S3
### locationparser.py:
Loads data about daily activty from raw file out of S3.  Includes a parsing of the data string to extract location and identifying data points.
### mapdemo.html
Web page for the demo couchapp which will display an interactive map, showing results for various users
### wifidemo
Database that holds the user activity log data points

http://bradwbonn.cloudant.com/wifidemo/

* URL of unique user ID's and their log counts.
https://bradwbonn.cloudant.com/wifidemo/_design/users/_view/usertrack?reduce=true&group_level=1&inclusive_end=false

### testfences
Database that holds the partner "fence" radii.
http://bradwbonn.cloudant.com/testfences/


