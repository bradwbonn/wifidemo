#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Script to demonstrate parallel geo query operations

# libraries
import requests, json, random
from time import time
from multiprocessing import Pool
from argparse import ArgumentParser
from os import environ

c = dict(
    # Set variables
    srcAPIKey = environ('WI2_CLOUDANT_API_KEY'), # APIキーは読み取り専用です
    srcDB = 'spapp',
    urlbase = "https://bradwbonn.cloudant.com/"
)

def main():
    a = get_args()
    
    print " サンプルデータセットを取得しています。お待ちください"
    
    datapoints = get_point_set(a.datapoints)
    
    print " {0}データポイントが取得されました".format(len(datapoints))
    
    print " クエリは{0}つのスレッドで実行されます".format(a.threads)
    
    pool = Pool(a.threads)
    
    print " テストは今実行中です..."
    
    startTime = time()
    
    results = pool.map(query_task,datapoints)
    
    totalTime = time() - startTime
    
    totalFences = 0
    
    for fences in results:
        
        totalFences = totalFences + fences

    print " {0}秒で{1}の地理空間クエリが完了しました".format(round(totalTime,2),a.datapoints)
    print " {0}ジオフェンスマッチ".format(totalFences)

def get_args():
    # parameters: <number of data points> <number of threads>
    argparser = ArgumentParser(description = 'Parallel Geo Query Script')
    argparser.add_argument(
        'datapoints',
        type=int,
        help="Number of data points to sample from spapp DB"
    )
    argparser.add_argument(
        'threads',
        type=int,
        help="Number of threads to run query test with",
        default=8
    )
    myargs = argparser.parse_args()
    return myargs
    
# Obtain a list of specified device check-in points from 'spapp' Cloudant database starting at a random skip value
def get_point_set(pointCount):
    skip = random_skip(pointCount)
    r = requests.get(
        url = "{0}{1}/_all_docs".format(c['urlbase'], c['srcDB']),
        params = {
            'limit': pointCount,
            'skip': skip,
            'include_docs': 'true'
        },
        auth = c['srcAPIKey']
    )
    coordinateSet = []
    for row in r.json()['rows']:
        coordinateSet.append(row['doc']['geometry']['coordinates'])
    return coordinateSet

# Inside each task:
def query_task(datapoint):

    WKT = "point({0}+{1})".format(datapoint[0],datapoint[1])
    r = requests.get(
        url = "https://bradwbonn.cloudant.com/fencemaster/_design/geoIdx/_geo/newGeoIndex?g={0}".format(WKT),
        auth = c['srcAPIKey'],
        params = {
            'limit':20
        },
        headers = {'Content-Type': 'application/json'}
    )
    
    fencesFound = len(r.json()['rows'])
    
    # return this thread's fence found count
    return fencesFound
    

def random_skip(datapoints):
    # get doc count from db (hard-coded for speed right now)
    docCount = 924776
    # return random int between 0 and doc count - datapoints
    return random.randint(0,docCount - (datapoints + 1))
    
if __name__ == "__main__":
    main()