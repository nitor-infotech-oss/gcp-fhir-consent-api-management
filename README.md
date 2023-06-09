![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)

# GCP FHIR Consent Management & Conformance Implementation - Accelerator

> This solution/accelerator helps in consuming GCP FHIR services in order to pull EHR data based on consent approval. Also, it includes option to push EHR data to FHIR store that gets validated against the conformance setup on FHIR store. This will provide an idea of how GCP and FHIR services can be integrated with any web app.


<br/>

# Table of contents
* [Prerequisites](#prerequisites)
  * Consent Management:
    * [Concepts and How-to Links for consent](#concepts-and-how-to-links-for-consent)
    * [Step by Step guide for GCP Healthcare API and FHIR resource setup](#step-by-step-guide-for-gcp-healthcare-api-and-fhir-resource-setup)
  * Conformance Implementation:
    * [Concepts and How-to Links for conformance](#concepts-and-how-to-links-for-conformance)
    * [Step by Step guide for conformance setup on FHIR server](#step-by-step-guide-for-conformance-setup-on-fhir-server)
* [Web Application Local Setup Guide](#web-application-local-setup-guide)
  * [Running the application](#running-the-application)
  * [Using the application](#using-the-application)


<br/>

# Prerequisites

## Concepts and How-to Links for consent

<details><summary>Below are the prerequisites of Consent Management API that are needed in the entire Consent management setup</summary>

- [Healthcare APIs that are enabled on GCP account](https://cloud.google.com/healthcare-api/docs)
- [GCP user account login](https://cloud.google.com/sdk/gcloud/reference/init)
- [Dataset, Fhir Store creation](https://cloud.google.com/healthcare-api/docs/how-tos/fhir#curl)
- [Loading the resources like patient, encounter etc. into this FHIR Store](https://cloud.google.com/healthcare-api/docs/how-tos/fhir-resources)
- [Consent Store creation](https://cloud.google.com/healthcare-api/docs/how-tos/consent-managing)
- [Consent policies configuration](https://cloud.google.com/healthcare-api/docs/how-tos/consent-policies)
- [Consent and consent artifact creation](https://cloud.google.com/healthcare-api/docs/how-tos/consent-creating)
- [Creating user data mappings](https://cloud.google.com/healthcare-api/docs/how-tos/consent-registering-user-data)
- [Fetching the FHIR Store data](https://cloud.google.com/healthcare-api/docs/how-tos/fhir-resources)

</details>


<br/>

## Step by Step guide for GCP Healthcare API and FHIR resource setup

<details><summary>Step 1: Google Cloud Login</summary>

While using the local machine, we need to make sure that we are logged in to the GCP gcloud CLI with our user account by executing below auth login commands.
```bash
 gcloud init
```
OR
```bash
gcloud auth login
```
</details>

<details><summary>Step 2: GCP Dataset Creation</summary>

Before we can create a FHIR store, we need to create a dataset which we can using the following REST command by replacing capital letter words with our project specific values.
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "" \
    "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets?datasetId=DATASET_ID"
```
</details>

<details><summary>Step 3: GCP FHIR Store Creation</summary>

We need to save the request body in a file called request.json having the store version e.g R4. Run the following command in the terminal to create or overwrite this file in the current directory.
```bash
cat > request.json << 'EOF'
{
  "version": "FHIR_STORE_VERSION"
}
EOF
```
Then execute the following command to send our REST request for FHIR store creation.
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d @request.json \
    "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores?fhirStoreId=FHIR_STORE_ID"
```
</details>

<details><summary>Step 4: Loading FHIR resources into FHIR Data Store</summary>

We can load multiple resources in the FHIR store as per the steps 
below in which we have loaded the Patient, Encounter and Obervation data resources.
  - Patient Resource
  Save the request body in a file called request.json. Run the following command in the terminal to create or overwrite this file in the current directory:
  ```bash
  cat > request.json << 'EOF'
  {
    "name": [
      {
        "use": "official",
        "family": "Smith",
        "given": [
          "Darcy"
        ]
      }
    ],
    "gender": "female",
    "birthDate": "1970-01-01",
    "resourceType": "Patient"
  }
  EOF
  ```
  Then execute the following command to send our REST request for loading patient resource into FHIR store.
  ``` REST
  curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/fhir+json" \
      -d @request.json \
      "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores/FHIR_STORE_ID/fhir/Patient"
  ```
  - Encounter Resource
  Save the request body in a file called request.json. Run the following command in the terminal to create or overwrite this file in the current directory:
  ```bash
  cat > request.json << 'EOF'
  {
    "status": "finished",
    "class": {
      "system": "http://hl7.org/fhir/v3/ActCode",
      "code": "IMP",
      "display": "inpatient encounter"
    },
    "reasonCode": [
      {
        "text": "The patient had an abnormal heart rate. She was concerned about this."
      }
    ],
    "subject": {
      "reference": "Patient/PATIENT_ID"
    },
    "resourceType": "Encounter"
  }
  EOF
  ```
  Then execute the following command to send our REST request for loading patient resource into FHIR store.
  ``` REST
  curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/fhir+json" \
      -d @request.json \
      "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores/FHIR_STORE_ID/fhir/Encounter"
  ```
  - Observation Resource
  Save the request body in a file called request.json. Run the following command in the terminal to create or overwrite this file in the current directory:
  ```bash
  cat > request.json << 'EOF'
  {
    "resourceType": "Observation",
    "status": "final",
    "subject": {
      "reference": "Patient/PATIENT_ID"
    },
    "effectiveDateTime": "2020-01-01T00:00:00+00:00",
    "identifier": [
      {
        "system": "my-code-system",
        "value": "ABC-12345"
      }
    ],
    "code": {
      "coding": [
        {
          "system": "http://loinc.org",
          "code": "8867-4",
          "display": "Heart rate"
        }
      ]
    },
    "valueQuantity": {
      "value": 80,
      "unit": "bpm"
    },
    "encounter": {
      "reference": "Encounter/ENCOUNTER_ID"
    }
  }
  EOF
  ```
  Then execute the following command to send our REST request for loading patient resource into FHIR store.
  ``` REST
  curl -X POST \
      -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      -H "Content-Type: application/fhir+json" \
      -d @request.json \
      "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores/FHIR_STORE_ID/fhir/Observation"
  ```
</details>

<details><summary>Step 5: GCP Consent Store Creation</summary>

We need to save the request body in a file called request.json. Run the following command in the terminal to create or overwrite this file in the current directory.
```bash
cat > request.json << 'EOF'
{
  "defaultConsentTtl": "DEFAULT_CONSENT_EXPIRATION_DURATIONs",
  "enableConsentCreateOnUpdate": "ENABLE_CONSENT_CREATE_ON_UPDATE"
}
EOF
```
Then execute the following command to send our REST request for creating a consent store.
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d @request.json \
    "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores?consentStoreId=CONSENT_STORE_ID"
```
</details>

<details><summary>Step 6: Configure consent policies using RESOURCE and REQUEST attributes</summary>

- RESOURCE attributes
To create a RESOURCE attribute we need to send POST request using curl that creates attribute named data_identifiable with values identifiable and de-identified.
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H "Content-Type: application/consent+json; charset=utf-8" \
    --data "{
      'description': 'whether the data is identifiable',
      'category': 'RESOURCE',
      'allowed_values': [
        'identifiable',
        'de-identified'
      ],
    }" \
"https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/attributeDefinitions?attribute_definition_id=data_identifiable"
```
- REQUEST attributes
We need to send a POST request using curl that creates a REQUEST attribute named requester_identity:
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H "Content-Type: application/consent+json; charset=utf-8" \
    --data "{
      'description': 'what groups are consented for access',
      'category': 'REQUEST',
      'allowed_values': ['internal-researcher', 'external-researcher', 'clinical-admin'],
    }" \
"https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/attributeDefinitions?attribute_definition_id=requester_identity"
```
</details>

<details><summary>Step 7: Creating Consent Artifact</summary>

We can create consent artifacts using the following REST command on replacing with our values.
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H "Content-Type: application/consent+json; charset=utf-8" \
    --data "{
       'user_id': 'USER_ID',
       'user_signature' : {
         'user_id': 'USER_ID',
         'image': {
           'gcs_uri': 'gs://IMG_URI' },
         'signature_time': {
           'seconds': EPOCH_SECONDS },
      },
       'consent_content_screenshots': [
         { 'raw_bytes': 'BASE_64_IMAGE' }],
       'consent_content_version': 'v1',
       'metadata': {'client': 'mobile'}
    }" \
"https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/consentArtifacts"
```
</details>

<details><summary>Step 8: Creating a Consent</summary>

We can create a consent using the following REST command on replacing with our values.
``` REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H "Content-Type: application/consent+json; charset=utf-8" \
    --data "{
       \"user_id\": \"USER_ID\",
       \"policies\": [{
         \"resource_attributes\": [{
           \"attribute_definition_id\": \"data_identifiable\",
           \"values\": [\"identifiable\"]
         }],
         \"authorization_rule\": {
           \"expression\": \"requester_identity == 'clinical-admin'\",
        }
       },
       {
         \"resource_attributes\": [{
           \"attribute_definition_id\": \"data_identifiable\",
           \"values\": [\"de-identified\"]
         }],
         \"authorization_rule\": {
           \"expression\": \"requester_identity in ['internal-researcher', 'external-researcher']\"
          }
       }],
       \"consent_artifact\": \"projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/consentArtifacts/CONSENT_ARTIFACT_ID\",
       \"ttl\": \"EXPIRATION_DURATION\"
    }" \
"https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/consents"
```
</details>

<details><summary>Step 9: Creating the user data mappings</summary>

We can define data mappings using the following REST command on replacing with our values to register data with the Consent Management API and connected to consents.
```REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H "Content-Type: application/consent+json; charset=utf-8" \
    --data "{
       'user_id': 'USER_ID',
       'data_id' : 'DATA_ID',
       'resource_attributes': [{
           'attribute_definition_id': 'data_identifiable',
           'values': ['de-identified']
      }]
    }" \
"https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/userDataMappings"
```
Here 'DATA_ID' will be the data that the user data mapping resource refers e,g for FHIR resource it will be like 
```bash
  'data_id' : 'https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores/FHIR_STORE_ID/fhir/Patient/PATIENT_ID'
```
</details>

<details><summary>Step 10: Making Access Determinations</summary>

Under this our application can request access determinations from the Consent Management API for a specific data element, for all data elements associated with a user, or for whole data store by using following REST command.
```REST
curl -X POST \
    -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
    -H "Content-Type: application/consent+json; charset=utf-8" \
    --data "{
       'dataId' : 'DATA_ID',
       'requestAttributes': {
         'requesterIdentity': 'external-researcher'},
       'consentList':{
         'consents':[
           'projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID/consents/CONSENT_NAME'
         ]
       },
       'responseView': 'DETAILED_ACCESS_LEVEL'
    }" \
"https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/consentStores/CONSENT_STORE_ID:checkDataAccess"
```
</details>

<details><summary>Step 11: Fetching Data from FHIR Store</summary>

 We can get the contents of a particular FHIR resource using below REST API by replacing with our values.
- RESOURCE level like Patient, Encounter, Observation etc
```REST
curl -X GET \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores/FHIR_STORE_ID/fhir/Observation/OBSERVATION_ID"
```
- All RESOURCE associated with a particular patient data
```REST
curl -X GET \
     -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
     "https://healthcare.googleapis.com/v1/projects/PROJECT_ID/locations/LOCATION/datasets/DATASET_ID/fhirStores/FHIR_STORE_ID/fhir/Patient/PATIENT_ID/\$everything"
```
</details>


<br/>

## Concepts and How-to Links for conformance

<details>
  <summary>Below are the prerequisites of Confromance that are needed in the entire setup</summary>

- [Configure FHIR profiles](https://cloud.google.com/healthcare-api/docs/how-tos/fhir-profiles)

</details>


<br/>

## Step by Step guide for conformance setup on FHIR server

<details>
  <summary>Step 1: Defining FHIR profile</summary>

Refer detailed steps [here](https://cloud.google.com/healthcare-api/docs/how-tos/fhir-profiles#define_your_fhir_profiles) to define your profiles that involves downloading/configuring predefined structure definition, implementation guide and value sets and finally uploading & enabling the updated implementation guide for your FHIR store.

</details>

<details>
  <summary>Step 2: Validating resources against profile</summary>

Refer detailed steps [here](https://cloud.google.com/healthcare-api/docs/how-tos/fhir-profiles#validate_resources_against_specific_profiles) to validate a FHIR resource for a specific profile or for all profiles defined for your FHIR store.

</details>


<br/>

# Web Application Local Setup Guide

1. Clone the repository and change the directory to the repository folder
2. Create virtual environment `python -m venv .venv`
3. Activate virtual environment `source .venv/bin/activate`
4. Install dependencies `pip install -r requirements.txt`
5. Run database migrations `./manage.py migrate`

## Running the application
1. Activate virtual environment `source .venv/bin/activate`
2. Setup .env file by refering example.env file. You can clone example.env to create .env file within cmapi directory and then update it's content as per need.
3. Run the Django web application `./manage.py runserver`

## Using the application

#### Request Consent Endpoint
http://localhost:8000/

#### Approve Consent Endpoint
http://localhost:8000/consentapproval/

#### Manage Resources Endpoint
http://localhost:8000/manageresources/

#### Capability Statement Endpoint
http://localhost:8000/capabilitystatement/
