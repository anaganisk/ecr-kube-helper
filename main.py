import logging
import os
import sys
import boto3
import base64
import json

from kubernetes import client, config
from kubernetes.client.rest import ApiException


LOGLEVEL = os.environ.get('LOGLEVEL', 'DEBUG').upper()
TARGET_SECRET = os.environ.get('TARGET_SECRET')
TARGET_ECR = os.environ.get('TARGET_ECR')
TARGET_NAMESPACE = os.environ.get('TARGET_NAMESPACE')
TARGET_EMAIL = os.environ.get('TARGET_EMAIL', "docker@example.com")
TARGET_ANNOTATIONS = os.environ.get('TARGET_ANNOTATIONS', "{}")

logging.basicConfig(format='%(asctime)s - %(message)s', level=LOGLEVEL)

configuration = config.load_incluster_config()
v1 = client.CoreV1Api()

def get_ecr_credentials(registryids):
    client = boto3.client('ecr')
    response = client.get_authorization_token(
        registryIds= registryids
    )
    logging.debug(response)
    end_point = response["authorizationData"][0]["proxyEndpoint"]
    base64_message = response["authorizationData"][0]["authorizationToken"]
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    auth_data = message_bytes.decode('ascii').split(":")
    data = {
        "auths": {
            end_point: {
                "username": auth_data[0],
                "password": auth_data[1],
                "email": TARGET_EMAIL,
                "auth": response["authorizationData"][0]["authorizationToken"]
            }
        }
    }
    return json.dumps(data)


def create_secret(json_data):
    namespace = TARGET_NAMESPACE
    metadata = {
        "name": TARGET_SECRET,
        "namespace": TARGET_NAMESPACE,
        "annotations": json.loads(TARGET_ANNOTATIONS)
    }
    data = {
        ".dockerconfigjson": base64.b64encode(json_data.encode()).decode('ascii')
    }
    api_version = 'v1'
    kind = 'Secret'
    body = client.V1Secret(api_version, data, kind, metadata, type='kubernetes.io/dockerconfigjson')
    try:
        data = v1.create_namespaced_secret(TARGET_NAMESPACE, body)
        logging.debug(data)
    except ApiException as e:
        logging.error(e)

def delete_secret():
    try:
        data = v1.delete_namespaced_secret(TARGET_SECRET, TARGET_NAMESPACE)
        logging.debug(data)
    except ApiException as e:
        if e.status == "404":
            logging.debug("Non exisiting key, creating key")
            return None

def main():
    if TARGET_SECRET == None or TARGET_ECR == None:
        raise Exception('')
    else:
        ecr_creds = get_ecr_credentials([TARGET_ECR])
        delete_secret()
        create_secret(ecr_creds)

    

if __name__ == "__main__":
    logging.info("Fetching new credentials...")
    main()
else: 
    print("Run with main.py")
    sys.exit()
