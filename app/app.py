from flask import Flask, render_template, request, abort, jsonify, Response, url_for
from requests import get
from bson.objectid import ObjectId
from .config import Config
import boto3, re, time, os, pymongo
from bson.son import SON
from bson.regex import Regex
from pymarc import Record, JSONReader
from marctools.pymarcer import make_json
import time

# Initialize your application.
app = Flask(__name__)
bib_collection = Config.BIBS
auth_collection = Config.AUTHS

# Define Basic URL
URL_BY_DEFAULT='https://9inpseo1ah.execute-api.us-east-1.amazonaws.com/prod/symbol/'

# Define some variables

lst_pv=[]
dict_pv={}

def find_tag_sub_val(tag,code,val):
    #d = SON(data={'code':code, 'value': val})
    regex_val = SON(data={'$regex':Regex(val), '$options': 'i'})
    return_data = {
        'datafield': {
            '$elemMatch': {
                'tag': tag,
                'subfield': {
                    '$elemMatch':{
                        'code':code,'value': regex_val.to_dict()
                    }
                }    
            }
        }
    }
    return return_data

def generateSet(body,session):
    """
    Generate the set of data passing the parameters to the query
    """
    queryAA = {
        '$and': [
            find_tag_sub_val('191','a',body),
            find_tag_sub_val('992','a',session)
                ]
    }

    queryAAO = {
        '$and': [
            find_tag_sub_val('191','a',body),{
            '$or':[
            find_tag_sub_val('992','a',session),
            find_tag_sub_val('269','a',session)
                ]}]
    }

    for doc1 in bib_collection.find(queryAA):  
        reader=JSONReader(make_json(doc1))
        for pv in reader:
            try:
                dict_pv['symbol']=pv['191']['a']
                dict_pv['link']= URL_BY_DEFAULT+ pv['191']['a']
                dict_pv['title_a']=pv['245']['a']
                dict_pv['title_b']=pv['245']['b']
                dict_pv['created']=pv['998']['Z']
            except TypeError:
                dict_pv['symbol']=''
            try:
                dict_pv["date"]=pv['992']['a']
            except TypeError:
                dict_pv["date"]=''
            try:
                dict_pv["topic"]=pv['991']['d']
            except TypeError:
                dict_pv["topic"]=''
            lst_pv.append(dict_pv.copy())
            dict_pv.clear()

# Querying and displaying the results
@app.route("/fullcontent",methods=['POST','GET'])
def fullcontent():
    lst_pv.clear()
    myBody,mySession=request.form["body"],request.form["session"]
    body="^" 
    session="^"
    body += str(myBody)
    session+=str(mySession)
    startTime=time.time()
    generateSet(body,session)
    endTime=time.time()
    return(render_template('fullcontentplus.html',lst_pv=lst_pv,count=len(lst_pv),myTime=(endTime-startTime)))

# Parameter for the search 
@app.route('/')
@app.route('/fullcontentplus')
def fullcontentplus():
    return(render_template('fullcontentplus.html'))

# Main 

if __name__ == '__main__':
    app.debug=False
    app.run()
