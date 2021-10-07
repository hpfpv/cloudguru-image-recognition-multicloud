import json
from google.cloud import firestore

import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


subscription_key = os.environ["COMPUTER_VISION_SUB_KEY"]
endpoint = os.environ["COMPUTER_VISION_ENDPOINT"]
s3Bucket = os.environ["S3_BUCKET"]
analyze_url = endpoint + "vision/v3.1/analyze"

def getAnalysis(imageKey):

    db = firestore.Client()
    collection = db.collection(os.environ["FIRESTORE_COLLECTION"])
    documentId = str(imageKey).split('.', 1)[0]

    document = collection.document(documentId)

    response = document.get('analysis').to_dict()

    logger.info(json.dumps(response.json()))

    return json.dumps(response.json())

def lambda_handler(event, context):
    logger.info(event)
    
    imageKey = event['pathParameters']['imageKey']

    response = getAnalysis(imageKey)

    logger.info(response)

    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://imager.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET',
            'Content-Type': 'application/json'
        },
        'body': response
    }