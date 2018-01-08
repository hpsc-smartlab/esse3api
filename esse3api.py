# -*- coding: utf-8 -*-

#import json, sys, re, urllib, urllib2, socket, json, pydoc, cgi, os, time, inspect
#from hashlib import md5
#from datetime import datetime
#from bottle import Bottle,get,post,request
#from bottle import request

from flask import Flask
from flask import json
from flask import request
#from flask import Response
#from flask import request
from flask import jsonify
from flask import current_app
from flask import make_response
#from flask import session
#from flask import url_for
#from flask import redirect
#from flask import render_template
#from flask import abort
#from flask import g
#from flask import flash
#from flask import _app_ctx_stack
from datetime import timedelta
from flask_cors import CORS

from functools import update_wrapper


from scraper import Scraper

app = Flask(__name__)
CORS(app)

#@app.route('/')
#def form():
#    html='<p>Inserisci username e password istituzionale per testare l'' API</p><br><form action="/pagamenti" method="post"><input name="username"><input type="password" name="password"><input type="submit"></form>'
#    return html


def crossdomain(origin=None, methods=None, headers=None, max_age=21600,
                attach_to_all=True, automatic_options=True):
    """Decorator function that allows crossdomain requests.
      Courtesy of
      https://blog.skyred.fi/articles/better-crossdomain-snippet-for-flask.html
    """
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        """ Determines which methods are allowed
        """
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        """The decorator function
        """
        def wrapped_function(*args, **kwargs):
            """Caries out the actual cross domain code
            """
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


#OK questa va bene
@app.route('/',methods=['POST','OPTIONS'])
@crossdomain(origin='*')
def login():
    datain = request.data;
    dataDict = json.loads(datain)
    username = dataDict.get('matricola')
    password = dataDict.get('password')
    s = Scraper(username, password)
    return jsonify(s.login())

#ok questa va bene
@app.route('/libretto',methods=['POST','OPTIONS'])
@crossdomain(origin='*')
def libretto() :
    datain = request.data
    dataDict = json.loads(datain)
    username = dataDict.get('matricola')
    password = dataDict.get('password')
#    username = request.form['matricola']
#    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.libretto())

#ok questa va bene
@app.route('/riepilogo',methods=['POST'])
def riepilogo():
    datain = request.data
    dataDict = json.loads(datain)
    username = dataDict.get('matricola')
    password = dataDict.get('password')
#    username = request.form['matricola']
#    password = request.form['password']
    s = Scraper(username,password)
    return jsonify(s.riepilogo_esami())

#Ok questa va bene
@app.route('/pannello',methods=['POST'])
def pannello():
    datain = request.data
    dataDict = json.loads(datain)
    username = dataDict.get('matricola')
    password = dataDict.get('password')
#    username = request.form['matricola']
#    password = request.form['password']
    s = Scraper(username,password)
    return jsonify(s.pannello_di_controllo())

#Ok questa va bene
@app.route('/piano',methods=['POST'])
def piano():
    datain = request.data
    dataDict = json.loads(datain)
    username = dataDict.get('matricola')
    password = dataDict.get('password')
#    username = request.form['matricola']
#    password = request.form['password']
    s = Scraper(username,password)
    return jsonify(s.piano())

@app.route('/pagamenti',methods=['POST'])
def pagamenti():
    datain = request.data
    dataDict = json.loads(datain)
    username = dataDict.get('matricola')
    password = dataDict.get('password')
#    username = request.form['matricola']
#    password = request.form['password']
    s = Scraper(username,password)
    return jsonify(s.pagamenti())

if __name__ == '__main__':
    app.debug = True
    app.run(host='193.205.230.8',port=5000)
