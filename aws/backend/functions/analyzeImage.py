import requests
import matplotlib.pyplot as plt
import json
from PIL import Image
from io import BytesIO
from google.cloud import firestore

import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


subscription_key = os.environ["COMPUTER_VISION_SUB_KEY"]
endpoint = os.environ["COMPUTER_VISION_ENDPOINT"]
s3Bucket = os.environ["S3_BUCKET"]
analyze_url = endpoint + "vision/v3.1/analyze"

def getImageKey(event):
    eventBody = json.dumps(event['Records'][0])
    data = json.loads(eventBody)
    imageKey = data['s3']['object']['key']

    logger.info(imageKey)

    return imageKey

def getImageAnalysis(imageKey):
    imageUrl = imageUrl = f'https://{s3Bucket}.s3.amazonaws.com/{str(imageKey)}'

    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = {'visualFeatures': 'Categories,Description,Color'}
    data = {'url': imageUrl}
    try:
        response = requests.post(analyze_url, headers=headers,
                                params=params, json=data)
        response.raise_for_status()

        response = json.dumps(response.json())
        logger.info(response)
        return response
    except Exception as er:
        logger.info(er)

def displayImageWithCaption(imageKey, analysis):
    imageUrl = imageUrl = f'https://{s3Bucket}.s3.amazonaws.com/{str(imageKey)}'
    image_caption = analysis["description"]["captions"][0]["text"].capitalize()

    # Display the image and overlay it with the caption.
    image = Image.open(BytesIO(requests.get(imageUrl).content))
    plt.imshow(image)
    plt.axis("off")
    _ = plt.title(image_caption, size="x-large", y=-0.1)
    plt.show()

def postImageDataToGCPFirestore(imageKey, analysis):
    imageUrl = imageUrl = f'https://{s3Bucket}.s3.amazonaws.com/{str(imageKey)}'
    imageUrlJson = {
        "imageUrl": imageUrl
    }
    data = {}
    data["imageUrl"] = imageUrlJson
    data["analysis"] = analysis
    logger.info(data)
    documentId = str(imageKey).split('.', 1)[0]
    db = firestore.Client()
    collection = db.collection(os.environ["FIRESTORE_COLLECTION"])
    document = collection.document(documentId).set(data)
    logger.info(document)


def lambda_handler(event, context):
    logger.info(event)
    # Grab image Url from s3
    imageKey = getImageKey(event)

    # Get image analysis
    analysis = getImageAnalysis(imageKey)

    # store imageUrl and analysis in GCP Firestore
    postImageDataToGCPFirestore(imageKey, analysis)

    logger.info(analysis)

    responseBody = {}
    responseBody["status"] = "success"
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': 'https://imager.houessou.com',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(responseBody)  
    }