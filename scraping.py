#!/usr/bin/python
import lxml.html
import requests
import json
import sys
import pymongo
import datetime 
import os
url = os.environ['url'] 
def find_by_xpath(url,xpath_expression):
    r = requests.get(url)
    if r.ok == False:
        raise ValueError('failed to retrieve url')
    element_source = r.text
    root = lxml.html.fromstring(element_source)
    tree = root.getroottree()
    return root.xpath(xpath_expression)

def setup(target, dictionary):
    temp = {}
    if target.attrib:
        for key, value in target.attrib.iteritems():
            temp[key]=value
    if target.text:
        temp["text"]=target.text
    dictionary[target.tag] = temp
def createJsonElement(target, dictionary):
    for child in target:
        setup(child, dictionary)
        createJsonElement(child, dictionary)
    return dictionary
def convertElementsToJSON(elements):
    tempArray = []
    WrapperDict = {}
    for elem in elements:
        if type(elem).__name__ != "_ElementStringResult":
            dictionary = {}
            if elem.attrib:
                for key, value in elem.attrib.iteritems():
                    dictionary[key]=value
            if elem.text:
                dictionary["text"]=elem.text
            tempArray.append(createJsonElement(elem, dictionary))
        else:
            tempArray.append({"href": elem})
    if type(elem).__name__ != "_ElementStringResult":
        WrapperDict[elements[0].tag]=tempArray
    else:
        WrapperDict["a"]=tempArray
    return WrapperDict

def insertTodb(item, db):
    anime = db["anime"]
    anime.insert_one(item)

def updateTodb(item, db, uri):
	anime = db["anime"]
	query = {'uri': uri}
	anime.update(query,{'$set': item})

def insertUrlTodb(item, db):
    anime = db["anime_urls"]
    anime.insert_one(item)

def getData(app,uri, xpath):
    try:
        completeDict = {}
        elements = find_by_xpath(uri, xpath)
        completeDict["uri"]= uri
        completeDict["updatedOn"]=datetime.datetime.utcnow()
        completeDict["data"]=convertElementsToJSON(elements)
     	client = pymongo.MongoClient(url)
     	db = client.get_default_database()
        insertTodb(completeDict,db)
        insertUrlTodb({"uri": uri, "xpath": xpath}, db)
        client.close()
        return {'succdeed': True, 'data': completeDict["data"]}
    except Exception as error:
        app.logger.warning(error)
        return {'succdeed': False}

def getDataLocal(uri, xpath):
    try:
        completeDict = {}
        elements = find_by_xpath(uri, xpath)
        completeDict["data"]=convertElementsToJSON(elements)
        completeDict["updatedOn"]=datetime.datetime.utcnow()
     	client = pymongo.MongoClient(url)
     	db = client.get_default_database()
        updateTodb(completeDict,db, uri)
        client.close()
        return True
    except Exception as error:
        print error
        return False

def ChronTask():
	client = pymongo.MongoClient(url)
 	db = client.get_default_database()
 	for urlObj in db["anime_urls"].find():
 		print urlObj["uri"]
   		getDataLocal(urlObj["uri"], urlObj["xpath"])
   	print "done Task"
   	client.close()