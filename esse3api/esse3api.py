
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

from flask_restplus import Resource, Api
from flask_restplus import fields

from functools import wraps
from functools import update_wrapper

import logging
import traceback

log = logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
app.config.from_object(__name__) # load config from this file , esse3api.py

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('ESSE3API_SETTINGS', silent=True)

@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.exception(message)

    if not settings.FLASK_DEBUG:
        return {'message': message}, 500

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

parser = api.parser()
parser.add_argument('username', help='The username', location='form')
parser.add_argument('password', help='The passowrd', location='form')

@api.route('/dati_anagrafici')
class DatiAnagrafici(Resource):
    @api.doc(parser=parser)
    def post(self):
        """Recuper i dati anagrafici
        :param: username: Nome utente
        :param: password: Password

        :example: /dati_anagrafici

        :returns:  json -- I dati personali
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        log.info(username)
        
        s = Scraper(username, password)
        return jsonify(s.dati_anagrafici())   

@api.route('/login')
class Login(Resource):
    @api.doc(parser=parser)
    def post(self):
        """Permette il login al portale esse3
        :param: username: Nome utente
        :param: password: Password

        :example: /login

        :returns:  json -- Risultato del login
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.login())

@api.route('/riepilogo_esami')
class RiepilogoEsami(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce il riepilogo degli esami effettuati dallo studente
        :param: username: Nome utente
        :param: password: Password

        :example: /riepilogo_esami

        :returns:  json -- Lista degli esami sostenuti
        -------------------------------------------------------------------------------------------
        """
        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.riepilogo_esami())

@api.route('/residenza')
class Residenza(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce la residenza dello studente
        :param: username: Nome utente
        :param: password: Password

        :example: /residenza

        :returns:  json -- Residenza dello studente
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.residenza())

@api.route('/domicilio')
class Domicilio(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce il domicilio dello studente
        :param: username: Nome utente
        :param: password: Password

        :example: /domicilio

        :returns:  json -- Domicilio dello studente
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.domicilio())

@api.route('/libretto')
class Libretto(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce il libretto universitario dello studente
        :param: username: Nome utente
        :param: password: Password
    
        :example: /libretto
    
        :returns:  json -- Libretto dello studente
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.libretto())

@api.route('/pagamenti')
class Pagamenti(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce i pagamenti effettuati dello studente
        :param: username: Nome utente
        :param: password: Password

        :example: /pagamenti

        :returns:  json -- Pagamenti effettuati dallo studente
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.pagamenti())

@api.route('/prenotazioni_effettuate')
class PrenotazioniEffettuate(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce le prenotazioni alle sedute d'esame effettuati dello studente
        :param: username: Nome utente
        :param: password: Password

        :example: /prenotazioni_effettuate

        :returns:  json -- Prenotazioni effettuate dallo studente
        -------------------------------------------------------------------------------------------
        """

        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.prenotazioni_effettuate())

@api.route('/piano')
class Piano(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce il piano di studio dello studente
        :param: username: Nome utente
        :param: password: Password

        :example: /piano

        :returns:  json -- Lista degli esami sostenuti
        -------------------------------------------------------------------------------------------
        """
        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.piano())

@api.route('/pannello')
class Piano(Resource):
    @api.doc(parser=parser)
    def post(self) :
        """Restituisce il pannello di controllo dello studente
        :param: username: Nome utente
        :param: password: Password

        :example: /pannello

        :returns:  json -- Lista degli esami sostenuti
        -------------------------------------------------------------------------------------------
        """
        args = parser.parse_args(strict=True)
        username = args['username']
        password = args['password']

        s = Scraper(username, password)
        return jsonify(s.pannello_di_controllo())

if __name__ == '__main__':
    app.debug = True
    app.run()
