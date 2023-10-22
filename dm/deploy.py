import oyaml as yaml
import json
import os
import requests
import subprocess
from datetime import datetime
import uuid
from time import sleep
from pprint import pprint

# function to return a uuid
def get_uuid() -> str:
    return str(uuid.uuid1())

def get_api_key() -> str:
    return os.environ.get('EC_API_KEY')

def headers() -> dict:
    return {'Authorization': f"ApiKey {get_api_key()}"}

def template(template_id) -> dict:
    with open(f"templates/{template_id}.json") as f:
        return json.load(f)
    
def payload(template_id='minimal') -> dict:
    return set_name(tag(template(template_id)))

def set_name(payload):
    payload['name'] = get_uuid()
    return payload

def get_ip() -> str:
    return subprocess.run(['curl', 'ifconfig.me'], capture_output=True).stdout.decode('utf-8').strip()

def tag(t) -> dict:
    t['metadata'] = {'tags': []}
    t['metadata']['tags'].append({"key": "requesting_ip", "value": get_ip()})
    t['metadata']['tags'].append({"key": "request_timestamp", 
                                  "value": str(datetime.now().isoformat(timespec='microseconds'))})
    return t

def url(path) -> str:
    return f"{config['ec_api_url']}/{path}"

def make_deployment(template_id) -> requests.Response:
    return requests.post(url('deployments'), 
                             headers=headers(), 
                             json=payload(template_id))

def shutdown_deployment(deployment_id) -> requests.Response:
    return requests.post(url(f"deployments/{deployment_id}/_shutdown"), 
                             headers=headers())

def get_deployment(deployment_id) -> requests.Response:
    return requests.get(url(f"deployments/{deployment_id}"), 
                             headers=headers())

def update_status() -> None:
    pass    

def start_timer() -> None:
    pass

def time_remaining() -> None:
    pass

def add_grace_time() -> None:
    pass

def log(response) -> None:
    with open('log.json', 'a') as f:
        f.write(json.dumps({'status_code': response.status_code }) + '\n')
        f.write(json.dumps(response.json()) + '\n')

def get_config(filename='config.yaml') -> dict:
    file = os.path.dirname(os.path.abspath(__file__)) + '/config/' + filename
    with open(file) as f:
        config = yaml.safe_load(f)
    return config

def healthy(response) -> bool:
    return response.status_code == 200 and response.json()['healthy'] == True

def wait_for_deployment(deployment_id) -> None:
    response = get_deployment(deployment_id)
    while not healthy(response):
        sleep(30)
        response = get_deployment(deployment_id)
    log(response)
    return response

def get_service_url(response) -> str:
    if response.status_code == 200:
        return response.json()['resources']['kibana'][0]['info']['metadata']['service_url']
    else:
        return None

def get_credentials(response) -> dict:
    if response.status_code == 201:
        return {'username': response.json()['resources'][0]['credentials']['username'],
                'password': response.json()['resources'][0]['credentials']['password']}
    else:
        return None

if __name__ == '__main__':
    config = get_config()
    response = make_deployment('minimal')
    login_info = get_credentials(response)
    created = wait_for_deployment(response.json()['id'])
    login_info['service_url'] = get_service_url(created)
    pprint(login_info)

