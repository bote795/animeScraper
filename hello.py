from flask import Flask, request, jsonify
import sys
from urllib import unquote
from flask_pymongo import PyMongo
from scraping import getData, returnScrape
import logging
import os
from logging.handlers import RotatingFileHandler
app = Flask(__name__)
app.debug=True

url = os.environ['url'] 
app.config["MONGO_URI"]=url
mongo = PyMongo(app)

@app.route("/uris")
def getUris():
    data = []
    paramUri=request.args.getlist('uri')
    for param in paramUri:
        param = unquote(param);
        temp = mongo.db["anime"].find_one({'uri': param })
        if temp is not None: #check if noneType
            temp.pop("_id")
            data.append(temp)
    return jsonify({"status": "ok", "data": data})

@app.route("/uri")
def getAllUris():
    data = []
    data2= mongo.db["anime_urls"].find()
    for item in data2:
        if item is not None: #check if noneType
            item.pop("_id")
            data.append(item)
    return jsonify({"status": "ok", "data": data})

@app.route("/uri" , methods=['DELETE'])
def deleteUri():
    try:
        value = unquote(request.args.get('uri'))
        result = mongo.db["anime_urls"].delete_one( { "uri": value })
        return jsonify({"status": "ok"})
    except Exception as error:
        return jsonify({"status": "fail"})

@app.route('/addUri', methods=['POST'])
def addUri():
    result = getData(app,request.form['uri'],request.form["xpath"].encode('utf-8'))
    if result["succdeed"]:
        return jsonify({"status": "ok", 'data': result["data"]})
    else:
        return jsonify({"status": "fail"})

@app.route('/testScrape', methods=['POST'])
def testUri():
    result = returnScrape(app,request.form['uri'],request.form["xpath"].encode('utf-8'))
    if result["succdeed"]:
        return jsonify({"status": "ok", 'data': result["data"]})
    else:
        return jsonify({"status": "fail"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)