import base64
import os
import requests
import urllib

from flask import Flask, render_template, session, redirect, url_for, flash, request, abort
from flask_wtf.csrf import CsrfProtect

from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment

from forms import AuthDBForm, NewProjectForm

from dropboxAPI import (get_info, get_team_members, get_dropbox_groups, get_user_account_detail,
						get_file_or_folder_metadata, create_dropbox_folder, list_folder_content,
						get_folders_to_create, create_folders, share_dropbox_folder, add_dropbox_share_permissions)

app = Flask(__name__)
#Breaks Heroku
#app.config['SECRET_KEY'] = os.urandom(24)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['DEBUG'] = os.environ['DEBUG']
AUTH_REDIRECT_SCHEME = os.environ['AUTH_REDIRECT_SCHEME']

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

csrf = CsrfProtect()

#Dropbox App
APP_KEY = os.environ['APP_KEY']
APP_SECRET = os.environ['APP_SECRET']

#Read Dropbox Business API key from OS or Heroku config var:
DB_BUSINESS_AUTH = os.environ['DB_AUTH']

#Static template folder till we get some front end code to do this:
template_folder = "/Project_Automation_Template"

csrf_token = base64.urlsafe_b64encode(os.urandom(18))

@app.route('/')
def index():
	session['csrf_token'] = csrf_token
	return render_template('index.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth(): 	
	form = AuthDBForm()
	if form.validate_on_submit():
		return redirect('https://www.dropbox.com/1/oauth2/authorize?%s' % urllib.urlencode({
			'client_id': APP_KEY,
			'redirect_uri': url_for('db_auth_finish', _external=True, _scheme=AUTH_REDIRECT_SCHEME),
			'response_type': 'code',
			'state': csrf_token
			}))
	return render_template('main.html', form=form)


@app.route('/db_auth_finish', methods=['GET', 'POST'])
def db_auth_finish():
	#if request.args['state'] != session.pop('csrf_token'):
	#	abort(403)
	data = requests.post('https://api.dropbox.com/1/oauth2/token',
			data={
			'code': request.args['code'],
			'grant_type': 'authorization_code',
			'redirect_uri': url_for('db_auth_finish', _external=True, _scheme=AUTH_REDIRECT_SCHEME)},
			auth=(APP_KEY, APP_SECRET)).json()
	session['dropbox_user_token'] = data['access_token']
	return redirect(url_for('main'))


@app.route('/complete', methods=['GET', 'POST'])
def complete(form=None):
	top_level_folder_to_create = form.project_name.data
	rw_group = form.project_rw_members.data
	ro_group = form.project_ro_members.data
	folder_content = list_folder_content(session['dropbox_user_token'], template_folder)
	folders_to_create = get_folders_to_create(folder_content, template_folder, top_level_folder_to_create)
	create_folders(session['dropbox_user_token'], folders_to_create)
	shared_folder_detail = share_dropbox_folder(session['dropbox_user_token'], folders_to_create[0])
	perms_change_status_rw = add_dropbox_share_permissions(session['dropbox_user_token'], shared_folder_detail['shared_folder_id'], rw_group, "editor")
	perms_change_status_ro = add_dropbox_share_permissions(session['dropbox_user_token'], shared_folder_detail['shared_folder_id'], ro_group, "viewer")
	return render_template('complete.html', folder_content=folders_to_create, project_name=top_level_folder_to_create)


@app.route('/main', methods=['GET', 'POST'])
def main():
	if 'dropbox_user_token' not in session:
		return redirect('/')
	newProjectForm = NewProjectForm()

	dropbox_groups = get_dropbox_groups(DB_BUSINESS_AUTH)
	newProjectForm.project_rw_members.choices = [ (g['group_id'], g['group_name']) for g in dropbox_groups['groups']]
	newProjectForm.project_ro_members.choices = [ (g['group_id'], g['group_name']) for g in dropbox_groups['groups']]

	if newProjectForm.validate_on_submit():
		return complete(newProjectForm)

	basic_team_information = get_info(DB_BUSINESS_AUTH)
	user_account_detail = get_user_account_detail(session['dropbox_user_token'])
	template_folder_info = get_file_or_folder_metadata(session['dropbox_user_token'], template_folder)
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
	csrf.init_app(app)

