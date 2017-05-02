#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# geoquery.py
# Sample Wi2 Geo query demo script

# Query for overlapping geofences based on current location of user mobile device

# OOO:
# Input coordinates of user device or use pre-selected locations
# Show query structure
# Show actual query URL
# Run query and return clean result
# Display raw JSON response

import json
import requests
from pprint import pprint
from sys import exit
from time import time

def main():
    myAccount = "bradwbonn"
    myDB = "fencemaster"
    myDDoc = "geoIdx"
    myIndex = "newGeoIndex"
    myCoords = chooseCoordinates()
    myRelation = getRelationType()
    myQuery = showQuery(myCoords, myRelation, myAccount, myDB, myDDoc, myIndex)
    myJSON = getFences(myQuery)
    showResponse(myJSON)
    
def chooseCoordinates():
    print "\n 以下のオプションから座標を選択してください:"
    print " 1. 羽田空港ターミナル Haneda Airport Terminal"
    print " 2. 大仏鎌倉 Great Buddha Kamakura"
    print " 3. Wi2 企業のオフィス"
    print " 4. カスタム選択"
    menuOption = int(raw_input(" (1-4) > "))
    if menuOption == 1:
        return [139.78111267089844, 35.55436500410275]
    if menuOption == 2:
        return [139.535700, 35.316698]
    if menuOption == 3:
        return [139.769246, 35.673325]
    if menuOption == 4:
        longitude = raw_input(" 入力経度してください: ")
        latitude = raw_input(" 入力してください緯度: ")
        return [longitude, latitude]

def getRelationType():
    print "\n オプションを選択してください: "
    print " 1. contains 含む"
    print " 2. intersects 交わる"
    print " 3. nearest 最寄り"
    return int(raw_input(" (1-3) > "))

def showQuery(coords, relation, account, db, ddoc, index):
    print "\n データベースクエリURI: "
    WKT = "point({0}+{1})".format(coords[0],coords[1])
    queryString = "https://{0}.cloudant.com/{1}/_design/{2}/_geo/{3}?g={4}&limit=50".format(account,db,ddoc,index,WKT)
    if relation == 1:
        queryString = queryString + "&relation=contains"
    elif relation == 2:
        queryString = queryString + "&relation=intersects"
    elif relation == 3:
        queryString = "{0}&nearest=true".format(queryString)
    print queryString
    return queryString

def getFences(query):
    startTime = time()
    r = requests.get(
        query,
        headers = {'Content-Type': 'application/json'},
        # APIキーは読み取り専用です
        auth = ("tinetiffeencesidetteryto","1d181a41ebbe621ad2cf7fd5780261efeae17c7e")
    )
    endTime = time()
    print "\n 実行パフォーマンス: {0} 秒".format(round((endTime - startTime),2))
    return r.json()

def showResponse(jsonResponse):
    if len(jsonResponse['rows']) == 0:
        exit("\n 一致する地理空間エンティティはありません No geo entities match")
    print "\n この場所はジオフェンスにあります"
    for row in jsonResponse['rows']:
        print " " + row['id']
    showMe = raw_input("\n JSONを見たいですか？(y/n) > ")
    if showMe == "y" or showMe == "Y":
        print "\n JSONレスポンス:"
        pprint(jsonResponse)

if __name__ == "__main__":
    main()