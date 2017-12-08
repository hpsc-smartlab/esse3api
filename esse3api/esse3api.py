
import json, sys, re, urllib, urllib2, socket, json, pydoc, cgi, os, time, inspect
from hashlib import md5
from datetime import datetime

import time
import csv
from scraper import Scraper
from flask import Flask
from flask import Response
from flask import request
from flask import jsonify
from flask import current_app
from flask import make_response
from flask import session
from flask import url_for
from flask import redirect
from flask import render_template
from flask import abort
from flask import g
from flask import flash
from flask import _app_ctx_stack

from functools import wraps
from functools import update_wrapper

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , esse3api.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('ESSE3API_SETTINGS', silent=True)

#### CROSSDOMAIN DECORATOR ####
def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
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
            h['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator

#### JSONP DECORATOR ####
def jsonp(func):
    """ Wrap json as jsonp """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Shows the home page
    """
    actions=[]
    my_path=os.path.abspath(inspect.getfile(inspect.currentframe()))
    print "my_path:"+my_path
    with open(my_path) as f:
        add=False
        action=None
        for line in f:
            line=line.lstrip()
            if line.startswith("@app."):
                line=line.replace("@app.","").replace("'",'"').replace("\n","")
                method=None
                if line.startswith("route"):
                    method="get"
                    path=re.findall(r'"([^"]*)"', line)[0]
                    if path != '/':
                        action={"method":method,"url":cgi.escape(path),"params":[]}
            elif line.startswith('"""') and action is not None:
                if add is False:
                    add=True
                    action['title']=line.replace('"""','').strip()
                else:
                    add=False
                    actions.append(action)
                    action=None
            elif line.startswith("@jsonp"):
                action['jsonp']=True
            elif line.startswith("@crossdomain"):
                action['crossdomain']=True
            else:
                if add is True:
                    if ":example:" in line:
                        line=line.replace(":example:","").strip()
                        action['example']=request.host+line
                    elif line.startswith(":param"):
                        line=line.replace(":param:","").strip()
                        name=line.split(":")[0]
                        desc=line.split(":")[1]
                        action['params'].append({"name":name,"desc":desc})
                    elif line.startswith(":returns:"):
                        line=line.replace(":returns:","").strip()
                        action['returns']=line
                    else:
                        pass
    return render_template('layout.html',actions=actions)

@app.route('/test')
def hello_world():
    html='<p>Inserisci username e password istituzionale per testare l'' API</p><br><form action="/prenotazioni_effettuate" method="post"><input name="username"><input type="password" name="password"><input type="submit"></form>'
    return html

@app.route('/dati_personali',methods=['POST'])
@jsonp
def dati_personali() :
    """Restituisce i dati personali
    :param: username: Nome utente
    :param: password: Password

    :example: /dati_personali

    :returns:  json -- I dati dello studente
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.dati_personali())

@app.route('/login',methods=['POST'])
@jsonp
def login():
    """Permette il login al portale esse3
    :param: username: Nome utente
    :param: password: Password

    :example: /login

    :returns:  json -- Risultato del login
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.login())

@app.route('/riepilogo_esami',methods=['POST'])
@jsonp
def riepilogo_esami() :
    """Restituisce il riepilogo degli esami effettuati dallo studente
    :param: username: Nome utente
    :param: password: Password

    :example: /riepilogo_esami

    :returns:  json -- Lista degli esami sostenuti
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.riepilogo_esami())

@app.route('/residenza',methods=['POST'])
def residenza() :
    """Restituisce la residenza dello studente
    :param: username: Nome utente
    :param: password: Password

    :example: /residenza

    :returns:  json -- Residenza dello studente
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.residenza())

@app.route('/domicilio',methods=['POST'])
def domicilio() :
    """Restituisce il domicilio dello studente
    :param: username: Nome utente
    :param: password: Password

    :example: /domicilio

    :returns:  json -- Domicilio dello studente
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.domicilio())

@app.route('/libretto',methods=['POST'])
def libretto() :
    """Restituisce il libretto universitario dello studente
    :param: username: Nome utente
    :param: password: Password

    :example: /libretto

    :returns:  json -- Libretto dello studente
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.libretto())

@app.route('/pagamenti',methods=['POST'])
def pagamenti() :
    """Restituisce i pagamenti effettuati dello studente
    :param: username: Nome utente
    :param: password: Password

    :example: /pagamenti

    :returns:  json -- Pagamenti effettuati dallo studente
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.pagamenti())

@app.route('/prenotazioni_effettuate',methods=['POST'])
def prenotazioni_effettuate() :
    """Restituisce le prenotazioni alle sedute d'esame effettuati dello studente
    :param: username: Nome utente
    :param: password: Password

    :example: /prenotazioni_effettuate

    :returns:  json -- Prenotazioni effettuate dallo studente
    -------------------------------------------------------------------------------------------

    """
    username = request.form['username']
    password = request.form['password']
    s = Scraper(username, password)
    return jsonify(s.prenotazioni_effettuate())

if __name__ == '__main__':
    app.debug = True
    app.run()
