import json
import logging
import subprocess
from datetime import datetime

from django.conf import settings
from requests import request

log = logging.getLogger(__name__)

CONSENT_NAME_TEMPLATE = settings.CONSENT_NAME_TEMPLATE
USER_CONSENT_ARTIFECT = settings.USER_CONSENT_ARTIFECT
CONSENT_BASE_URL = settings.CONSENT_BASE_URL
EVALUATE_CONSENT_URL = settings.EVALUATE_CONSENT_URL
FHIR_STORE_URL = settings.FHIR_STORE_URL


def generate_policy(roles):
    policies = {
        'clinical-admin': {
            "resourceAttributes": [
                {
                    "attributeDefinitionId": "data_identifiable_1",
                    "values": [
                        "Patient",
                        "AllergyIntolerance",
                        "Encounter",
                        "Observation",
                    ]
                }
            ],
            "authorizationRule": {
                "expression": "requester_identity == 'clinical-admin'"
            }
        },
        'internal-researcher': {
            "resourceAttributes": [
                {
                    "attributeDefinitionId": "data_identifiable_1",
                    "values": [
                        "Patient",
                        "AllergyIntolerance"
                    ]
                }
            ],
            "authorizationRule": {
                "expression": "requester_identity == 'internal-researcher'"
            }
        },
        'external-researcher': {
            "resourceAttributes": [
                {
                    "attributeDefinitionId": "data_identifiable_1",
                    "values": [
                        "AllergyIntolerance",
                        "Encounter",
                        "Observation"
                    ]
                }
            ],
            "authorizationRule": {
                "expression": "requester_identity in ['external-researcher']"
            }
        }
    }

    generated_policies = []
    for role in roles:
        generated_policies.append(policies[role])

    return generated_policies


def get_headers():
    TOKEN = subprocess.check_output('gcloud auth print-access-token', shell=True).strip().decode("utf-8")
    return {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f'Bearer {TOKEN}'
    }


def get_consent(consent_id):
    response = {
        'error': False,
        'data': {},
        'message': ''
    }

    consent_url = '{}/{}'.format(CONSENT_BASE_URL, consent_id)
    r = request("GET", consent_url, headers=get_headers())
    log.info('gcp FHIR get_consent status: {}'.format(r.status_code))

    r_json = r.json()
    log.debug(r_json)

    if r.status_code == 200:
        if not r_json.get('expireTime'):
            # This is to enforce rule - Always have consent with expiry
            response['error'] = True
            response['message'] = 'Consent not allowed without any expiry'
            return response
        expireTime = datetime.strptime(r_json.get('expireTime')[:-4], '%Y-%m-%dT%H:%M:%S.%f')
        if datetime.now() >= expireTime:
            response['error'] = True
            response['message'] = 'Consent Expired'
            return response
        # return created consent id
        response['data'] = {
            'consent_id': r_json.get('name').split('/')[-1],
            'user_id': r_json.get('userId'),
            'expireTime': r_json.get('expireTime')
        }
    elif r.status_code == 401:
        #TODO: need to refresh token and retry api call
        response['error'] = True
        response['message'] = 'Unauthorized access'
    else:
        response['error'] = True
        response['message'] = r_json.get('error', {}).get('message', 'Unexpected error occurred')

    return response


def create_consent(user_id, requested_role, ttl='120s'):
    response = {
        'error': False,
        'data': {},
        'message': ''
    }

    payload = {
        "userId": user_id,
        "policies": generate_policy([requested_role]),
        "ttl": ttl,
        "consent_artifact": USER_CONSENT_ARTIFECT
    }

    r = request("POST", CONSENT_BASE_URL, headers=get_headers(), data=json.dumps(payload))
    log.info('gcp FHIR create_consent status: {}'.format(r.status_code))

    r_json = r.json()
    log.debug(r_json)

    if r.status_code == 200:
        # return created consent id
        response['data'] = {
            'consent_id': r_json.get('name').split('/')[-1]
        }
    elif r.status_code == 401:
        #TODO: need to refresh token and retry api call
        response['error'] = True
        response['message'] = 'Unauthorized access'
    else:
        response['error'] = True
        response['message'] = r_json.get('error', {}).get('message', 'Unexpected error occurred')

    return response


def get_data(user_id, requested_role, consent_id):
    response = {
        'error': False,
        'data': {},
        'message': ''
    }

    consent_response = get_consent(consent_id)
    if consent_response.get('error'):
        return consent_response
    consent_data = consent_response['data']

    consent_name = CONSENT_NAME_TEMPLATE.format(consent_id)

    payload = {
        'user_id' : user_id,
        'requestAttributes': {
            'requester_identity': requested_role
        },
        'consentList':{
            'consents':[
                consent_name
            ]
        },
        'responseView': 'FULL'
    }
    evaluation_data = request("POST", EVALUATE_CONSENT_URL, headers=get_headers(), data=json.dumps(payload))
    log.info('gcp FHIR get_data evaluation_data status: {}'.format(evaluation_data.status_code))

    evaluation_data_json = evaluation_data.json()
    log.debug(evaluation_data_json)

    allowed_data_ids = []
    if evaluation_data.status_code == 200:
        results = evaluation_data_json.get('results', [])
        allowed_data_ids = [
            result.get('dataId', '') \
                for result in results \
                    if result.get('consented', False) \
                        and result.get('consentDetails', {}).get(consent_name, {}).get('evaluationResult', '') == 'HAS_SATISFIED_POLICY'
        ]
    elif evaluation_data.status_code == 401:
        #TODO: need to refresh token and retry api call
        response['error'] = True
        response['message'] = 'Unauthorized access'
    else:
        response['error'] = True
        response['message'] = 'Consent Not Applicable'

    if response['error']:
        return response

    # FIXME: Collect valid data ids into a variable and pull data at once rather than making api calls in loop
    resources = []
    for data_id in allowed_data_ids:
        if not data_id:
            continue

        r = request("GET", data_id, headers=get_headers())
        log.info('gcp FHIR get_data status: {}'.format(r.status_code))

        r_json = r.json()
        log.debug(r_json)

        if r.status_code == 200:
            resources.append({
                'resource': r_json
            })
        elif r.status_code == 401:
            #TODO: need to refresh token and retry api call
            response['error'] = True
            response['message'] = 'Unauthorized access'
            break
        else:
            response['error'] = True
            response['message'] = r_json.get('issue', [{}])[0].get('diagnostics', 'Unexpected error occurred')
            break

    if response['error']:
        return response

    response['data'] = {
        'consent_data': consent_data,
        'patient_data': resources
    }

    return response
