import base64
import os
import requests
import urllib

from flask import Flask, render_template, session, redirect, url_for, flash, request

from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment 
from flask.ext.wtf import Form 

from datetime import datetime

from wtforms import StringField, SubmitField
from wtforms.validators import Required


app = Flask(__name__)
app.config['SECRET_KEY'] = '123SECRETi'
app.config['DEBUG'] = True
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

#Dropbox App
APP_KEY = 'uukptwu0r6kc0ok'
APP_SECRET = 'bctri5jlrgj0srj'
csrf_token = base64.urlsafe_b64encode(os.urandom(18))

class AuthDBForm(Form):
	submit = SubmitField('Authorize Access to Dropbox')


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/main', methods=['GET', 'POST'])
def main(): 	
	session['csrf_token'] = csrf_token
	form = AuthDBForm()
	if form.validate_on_submit():
		return redirect('https://www.dropbox.com/1/oauth2/authorize?%s' % urllib.urlencode({
			'client_id': APP_KEY,
			'redirect_uri': url_for('db_auth_finish', _external=True),
			'response_type': 'code',
			'state': csrf_token
			}))
	return render_template('main.html', form=form)


@app.route('/db_auth_finish', methods=['GET', 'POST'])
def db_auth_finish():
	if request.args['state'] != session.pop('csrf_token'):
		abort(403)
	data = requests.post('https://api.dropbox.com/1/oauth2/token',
			data={
			'code': request.args['code'],
			'grant_type': 'authorization_code',
			'redirect_uri': url_for('db_auth_finish', _external=True)},
			auth=(APP_KEY, APP_SECRET)).json()
	token = data['access_token']
	return render_template('main.html', db_auth=True, token=token)


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

if __name__ == '__main__':
	manager.run()

