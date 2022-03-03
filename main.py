from turtle import width
import requests
import json
import time
import pandas as pd

update = True


def reqManager(url):
    res = requests.get(url)
    if res.status_code == 429:
        print("Rate limitted, waiting 65s")
        time.sleep(65)
        res = req(url)
    else:
        return res


def getCollectionFromAPI():
    if update:
        req = reqManager(
            'https://' + 'api-mainnet.magiceden.dev/v2/launchpad/collections?offset=0&limit=500')
        jsondata = req.json()
        req2 = reqManager(
            'https://' + 'api-mainnet.magiceden.dev/v2/launchpad/collections?offset=500&limit=500')
        jsondata2 = req2.json()
        jsondata.extend(jsondata2)
    else:
        with open('collections.json', 'r') as collections_file:
            jsondata = json.load(collections_file)
    return pd.DataFrame(jsondata)


def sortData(data):
    data = data.sort_values(by="launchDatetime", ascending=False)

    ''' for i in range(len(data)):
        try:
            print(data[i]['launchDatetime'])
        except:
            data[i]['launchDatetime'] = ''
    '''
    return data


def updateFloorPrice(data):

    fplist = []
    for i in range(len(data)):
        # if "floorPrice" not in jsondata[i]:
        req = reqManager(
            "https://api-mainnet.magiceden.dev/v2/collections/"+data.symbol[i]+"/stats")
        print(req.status_code)
        req = req.json()
        try:
            fplist.append(round(req['floorPrice']*(0.1**9), 3))
        except:
            fplist.append(None)
    data['floorPrice'] = fplist

    return data


def removeUseless(data):
    data.drop('description', inplace=True, axis=1)
    data.drop('featured', inplace=True, axis=1)
    data.drop('image', inplace=True, axis=1)
    data.drop('edition', inplace=True, axis=1)
    return data


def printb(data):
    data = data.reindex(columns=["symbol", "name", "price",
                                 "floorPrice", "profit", "size", "launchDatetime"])
    from pretty_html_table import build_table
    html_table_blue_light = build_table(data, 'blue_dark', width="auto")
    with open('styled_table.html', 'w') as f:
        f.write(html_table_blue_light)


def updateProfit(data):
    profitList = []
    for i in range(len(data)):
        try:
            profitList.append(round(data['floorPrice'][i]-data['price'][i], 3))
        except:
            profitList.append(None)
    data['profit'] = profitList

    return data


data = getCollectionFromAPI()
data = updateFloorPrice(data)
data = updateProfit(data)

data = sortData(data)

datanew = removeUseless(data.copy())
printb(datanew)


data = data.to_json(orient="records")
datanew = datanew.to_json(orient="records")

with open('collections.json', 'w') as collections_file:
    collections_file.write(data)
with open('collectionsLight.json', 'w') as collections_file2:
    collections_file2.write(datanew)
