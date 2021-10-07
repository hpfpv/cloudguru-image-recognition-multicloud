import json
from google.cloud import firestore
import uuid

analysis = {
    "categories": [
        {
            "name": "others_",
            "score": 0.00390625
        }
    ],
    "color": {
        "dominantColorForeground": "Black",
        "dominantColorBackground": "Grey",
        "dominantColors": [
            "Grey",
            "Black"
        ],
        "accentColor": "956836",
        "isBwImg": False,
        "isBWImg": False
    },
    "description": {
        "tags": [
            "outdoor",
            "building",
            "statue",
            "street",
            "mammal",
            "city",
            "bovine"
        ],
        "captions": [
            {
                "text": "a statue of a bull",
                "confidence": 0.5581811666488647
            }
        ]
    },
    "requestId": "5983f942-6d70-4b00-bb64-cf89144a6d78",
    "metadata": {
        "height": 372,
        "width": 640,
        "format": "Jpeg"
    }
}

imageUrlJson = {
        "imageUrl": "imageUrlstring"
    }

data = {}
data["imageUrl"] = imageUrlJson
data["analysis"] = analysis

db = firestore.Client()
collection = db.collection('imager-houessou-com-analysis')
document = collection.document(str(uuid.uuid4())).set(data)
print(document)