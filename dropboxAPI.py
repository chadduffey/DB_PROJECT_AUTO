import json
import requests

#-------------------------
# Business API
#-------------------------

def get_info(token):
    dfbToken = "Bearer " + token
    try:
	    response = requests.post(url='https://api.dropboxapi.com/2/team/get_info',
	                    headers = ({ "Authorization" : dfbToken }))
    except:
    	return "get_info_failed"	
    
    return response.json()

def get_team_members(token):
	#need to correct this for teams > 1000 in production version via the cursor.
	#limiting to 100 for the demo.
	dfbToken = "Bearer " + token
	params = {"limit":100}
	try:
	    response = requests.post(url='https://api.dropboxapi.com/2/team/members/list',
	                    headers = ({ "Authorization" : dfbToken }))
	except:
		return "get_team_members_failed"

	return response.json()

def get_dropbox_groups(token):
	dfbToken = "Bearer " + token
	try:
	    response = requests.post(url='https://api.dropboxapi.com/2/team/groups/list',
	                    headers = ({ "Authorization" : dfbToken }))
	except:
		return "get_dropbox_groups_failed"

	return response.json()

#-------------------------
# Core API
#-------------------------

def get_user_account_detail(token):
	userToken = "Bearer " + token
	try:
	    response = requests.post(url='https://api.dropboxapi.com/2/users/get_current_account',
	                    headers = ({ "Authorization" : userToken }))
	except:
		return "get_user_account_detail_failed"

	return response.json()
