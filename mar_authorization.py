import requests
import logging

logging.info('===>Starting MAR Management Authorization Script')

# CONFIGURATION
# All server configuration fields will be available in the 'params' dictionary.
url = f'{params["connect_marmanagement_url"]}/api/token/pair'
username = params["connect_marmanagement_username"]
password = params["connect_marmanagement_password"]

# ***** START - AUTH API CONFIGURATION ***** #
auth_body = {
  "password": password,
  "username": username
}

#initialize response
response = {}

# Make the API Call
try:
    # Make the API Call
    resp = requests.post(
        url,
        json=auth_body,
        verify=ssl_verify,
        headers={'accept': 'application/json', 'Content-Type': 'application/json'},
    )

    # Return the 'response' dictionary, must have a 'succeded' field.

    if resp is None:
        response['succeeded'] = False
        response['result_msg'] = 'No response from MAR Management. Please check URL and service status.'
    elif resp.status_code == 200:
        response['succeeded'] = True
        response["token"] = resp.json()["access"]
        response['result_msg'] = f'Successfully connected to MAR Management and acquired JWT.'
    elif resp.status_code == 401:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received from MAR Management. Please check credentials!'
        logging.debug(resp.content)
    else:
        response['succeeded'] = False
        response['error'] = f'Error Code {resp.status_code} received MAR Management.'
        logging.debug(resp.content)

except Exception as e:
    response['succeeded'] = False
    response['token'] = ''
    response['error'] = "Could not connect to MAR Management. Exception: " + str(e)
    response['result_msg'] = "Could not connect to MAR Management. Exception: " + str(e)

# logging response for debugging purposes - you might disable this option later.
# logging.debug(f'Authorization Script Returned Response: {response}')
logging.info('===>Ending MAR Management Authorization Script')