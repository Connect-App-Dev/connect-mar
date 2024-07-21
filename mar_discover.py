import requests
import ipaddress
import datetime
import json
import time

# Get parameters
base_url = params["connect_marmanagement_url"]
token = params.get('connect_authorization_token', '')
recordsPerPage = int(params["connect_marmanagement_records_per_page"])
now = datetime.datetime.now()

logging.info("===> MAR Management: Start Host Discovery")

response = {
    "endpoints": []
}

# Endpoint object must look like:
# {
#   # Either mac or ip (or both) must be present
#   "mac": "string",
#   "ip": "string",
#   # a map/dictionary that contains host properties; the key will be the property name and the value will be the property value
#   "properties" : {}
# }

# Prepare to page through results
page = 0
totalRecords = recordsPerPage+1 # Force first request to fire; total records will be updated in response request
retry = 0
while((page+1)*recordsPerPage < totalRecords and retry < 3):
    # Allow 3 tries to make an api request before failing out totally
    retry += 1
    logging.debug(f'Making MAR request attempt {retry} for offset {page*recordsPerPage}')
    url = f'{base_url}/api/mar/?limit={recordsPerPage}&offset={page*recordsPerPage}'
    try:
        request = requests.get(
            url,
            verify=ssl_verify,
            headers={'Authorization': f'Bearer {token}'}
        )

        if(request.status_code == 200):
            response_json = request.json()
            logging.debug(f'MAR request for offset {page*recordsPerPage} succeded! Received {len(response_json["items"])} records in page. {response_json["count"]} records total to discover.')
            logging.debug(json.dumps(response_json))
            
            # keep track of paging
            totalRecords = response_json["count"]
            page += 1

            for entry in response_json['items']:
                logging.debug("Processing MAR Entry: " + entry['mac'])

                # Parse (required fields) time data
                created_date = datetime.datetime.strptime(entry['created_date'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
                modified_date = datetime.datetime.strptime(entry['modified_date'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
                effective_date = ""
                if "." in entry['effective_date']:
                    effective_date = datetime.datetime.strptime(entry['effective_date'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
                else:
                    effective_date = datetime.datetime.strptime(entry['effective_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)

                # create host record
                endpoint = {
                    "mac": entry['mac'],
                    "properties": {
                        "connect_marmanagement_entry_mac": True,
                        "connect_marmanagement_entry_last_seen": int(now.strftime('%s')),
                        "connect_marmanagement_entry_created": int(created_date.strftime('%s')),
                        "connect_marmanagement_entry_created_by": entry['created_by']['username'],
                        "connect_marmanagement_entry_modified": int(modified_date.strftime('%s')),
                        "connect_marmanagement_entry_modified_by": entry['modified_by']['username'],
                        "connect_marmanagement_entry_effective": int(effective_date.strftime('%s')),
                    }
                }

                # Add Properties if exist
                if entry['comment']:
                    endpoint["properties"]["connect_marmanagement_entry_comment"] = entry['comment']
                if entry['mar_comment']:
                    endpoint["properties"]["connect_marmanagement_entry_mar_comment"] = entry['mar_comment']
                if entry['group']:
                    endpoint["properties"]["connect_marmanagement_entry_group"] = {
                        "id": entry['group']['id'],
                        "name": entry['group']['name']
                    }
                if entry['template']:
                    endpoint["properties"]["connect_marmanagement_entry_template"] = {
                        "id": entry['template']['id'],
                        "name": entry['template']['name']
                    }
                if entry['category']:
                    endpoint["properties"]["connect_marmanagement_entry_category"] = {
                        "id": entry['category']['id'],
                        "name": entry['category']['name']
                    }
                if entry.get("authorization_parameters", False):
                    endpoint["properties"]["connect_marmanagement_entry_auth_params"] = {
                        "deny": entry.get('deny', False)
                    }
                    if entry.get('vlan_num', False):
                        endpoint["properties"]["connect_marmanagement_entry_auth_params"]["vlan_num"] = entry.get('vlan_num')
                    if entry.get('vlan_name', False):
                        endpoint["properties"]["connect_marmanagement_entry_auth_params"]["vlan_name"] = entry.get('vlan_name')
                if entry.get("expire_date", False):
                    expire_date = ""
                    if "." in entry['expire_date']:
                        expire_date = datetime.datetime.strptime(entry['expire_date'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc)
                    else:
                        expire_date = datetime.datetime.strptime(entry['expire_date'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc)
                    endpoint["properties"]["connect_marmanagement_entry_expire"] = int(expire_date.strftime('%s'))
                    endpoint["properties"]["connect_marmanagement_entry_has_expiration"] = True
                else:
                    endpoint["properties"]["connect_marmanagement_entry_has_expiration"] = False

                # Create host in response
                # logging.debug(json.dumps(endpoint))
                response['endpoints'].append(endpoint)
                # Reset retry tracker
                retry = 0
        else:
            logging.error("API Status code error: " + json.dumps(request.json()))
            time.sleep(retry * 0.2) # Delay retry
    except Exception as e:
        logging.error(f'Endpoint request for offset {page*recordsPerPage} failed: + {str(e)}')
        response["error"] = str(e)
        time.sleep(retry * 0.2) # Delay retry

logging.info("===> MAR Management: End Host Discovery")
# print(json.dumps(response['endpoints']))