import json
import logging
import subprocess

from django.conf import settings
from requests import request

log = logging.getLogger(__name__)
FHIR_STORE_URL = settings.FHIR_STORE_URL


def get_headers():
    TOKEN = subprocess.check_output('gcloud auth print-access-token', shell=True).strip().decode("utf-8")
    return {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {TOKEN}'
    }


def create_data(payload, type='Patient'):
    response = {
        'error': False,
        'data': {},
        'message': ''
    }

    r = request("POST", FHIR_STORE_URL+'/'+type, headers=get_headers(), data=json.dumps(payload))
    log.info('gcp FHIR create_data status: {}'.format(r.status_code))

    r_json = r.json()
    log.debug(r_json)

    if r.status_code == 201:
        response['message'] = 'Resource data uploaded successfully'
    elif r.status_code == 401:
        response['error'] = True
        response['message'] = 'Unauthorized access'
    elif r.status_code == 412:
        response['error'] = True
        response['message'] = 'Request rejected as resource data doesn\'t conform with the implementation guide.'
    else:
        response['error'] = True
        response['message'] = r_json.get('error', {}).get('message', 'Unexpected error occurred')

    return response


def get_fhir_metadata():
    response = {
        'error': False,
        'data': {},
        'message': ''
    }

    r = request("GET", FHIR_STORE_URL+'/metadata', headers=get_headers())
    log.info('gcp FHIR get_fhir_metadata status: {}'.format(r.status_code))

    r_json = r.json()
    log.debug(r_json)

    if r.status_code == 200:
        response['data'] = r_json
    elif r.status_code == 401:
        response['error'] = True
        response['message'] = 'Unauthorized access'
    else:
        response['error'] = True
        response['message'] = r_json.get('error', {}).get('message', 'Unexpected error occurred')

    return response
