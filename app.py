import base64
import os
import requests
import urllib

from flask import Flask, render_template, session, redirect, url_for, flash, request, abort

from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment 

from forms import AuthDBForm, NewProjectForm

from dropboxAPI import (get_info, get_team_members, get_dropbox_groups, get_user_account_detail,
						get_file_or_folder_metdata, create_dropbox_folder)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG'] = True

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

#Dropbox App
APP_KEY = 'k543xq496hfjkqw'
APP_SECRET = '6u1exxfq1aydw4m'

#Static template folder till we get some front end code to do this:
template_folder = "/Project_Automation_Template"

#Read Dropbox Business API key from OS or Heroku config var:
DB_BUSINESS_AUTH = os.environ['DB_AUTH']

csrf_token = base64.urlsafe_b64encode(os.urandom(18))

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth(): 	
	session['csrf_token'] = csrf_token
	form = AuthDBForm()
	if form.validate_on_submit():
		return redirect('https://www.dropbox.com/1/oauth2/authorize?%s' % urllib.urlencode({
			'client_id': APP_KEY,
			#once up on heroku we need to force scheme. 
			#'redirect_uri': url_for('db_auth_finish', _external=True, _scheme='https'),
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
			#once up on heroku we need to force scheme. 
			#'redirect_uri': url_for('db_auth_finish', _external=True, _scheme='https')},
			'redirect_uri': url_for('db_auth_finish', _external=True)},
			auth=(APP_KEY, APP_SECRET)).json()
	session['dropbox_user_token'] = data['access_token']
	return redirect(url_for('main'))

@app.route('/complete', methods=['GET', 'POST'])
def complete():
	return render_template('complete.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
	newProjectForm = NewProjectForm()
	
	dropbox_groups = get_dropbox_groups(DB_BUSINESS_AUTH)
	newProjectForm.project_rw_members.choices = [ (g['group_id'], g['group_name']) for g in dropbox_groups['groups']]
	newProjectForm.project_ro_members.choices = [ (g['group_id'], g['group_name']) for g in dropbox_groups['groups']]

	if newProjectForm.validate_on_submit():
		return redirect(url_for('complete'))#redirect(url_for('complete'))

	basic_team_information = get_info(DB_BUSINESS_AUTH)
	user_account_detail = get_user_account_detail(session['dropbox_user_token'])
	template_folder_info = get_file_or_folder_metdata(session['dropbox_user_token'], template_folder)
	if "error" in template_folder_info:
		if template_folder_info['error']['path']['.tag'] == 'not_found': 
			create_dropbox_folder(session['dropbox_user_token'], template_folder)

	session['account_id'] = user_account_detail['account_id']
	return render_template('main.html', db_auth=True, newProjectForm=newProjectForm,  
							user_detail=user_account_detail,
							basic_team_information=basic_team_information,
							template_folder=template_folder)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500

if __name__ == '__main__':
	app.run()

