import json
import requests

def get_info(token):
    dfbToken = "Bearer " + token
    try:
	    response = requests.post(url='https://api.dropboxapi.com/2/team/get_info',
	                    headers = ({ "Authorization" : dfbToken }))
    except:
    	return "get_info_failed"	
    
    return response.json()