import requests
import json

# Get parameters
url = f'{params["connect_marmgmt_url"]}/api/token/pair'
username = params["connect_marmgmt_username"]
password = params["connect_marmgmt_password"]

response = {
    "succeeded": False,
    "result_msg": ""
} 

auth_body = {
  "password": password,
  "username": username
}

try: 
    request = requests.post(
        url,
        verify=ssl_verify,
        headers={'accept': 'application/json', 'Content-Type': 'application/json'},
        json=auth_body
    )
    if(request.status_code == 200):
        response["succeeded"] = True
        response["result_msg"] = "Successfully authenticated!"
    else:
        response["succeeded"] = False
        response["result_msg"] = "API Status code error: " + json.dumps(request.json())
except Exception as e:
    response["succeeded"] = False
    response["result_msg"] = "Exception: " + str(e)

# logging.debug(response)