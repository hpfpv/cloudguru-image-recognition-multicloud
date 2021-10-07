import requests
import matplotlib.pyplot as plt
import json
from PIL import Image
from io import BytesIO


'''
Authenticate
Authenticates your credentials and creates a client.
'''
subscription_key = "13591f30175a4b79b4c8166496e55f64"
endpoint = "https://imager-houessou-com-computer-vision.cognitiveservices.azure.com/"
analyze_url = endpoint + "vision/v3.1/analyze"

url = "https://images.pexels.com/photos/338515/pexels-photo-338515.jpeg"
headers = {'Ocp-Apim-Subscription-Key': subscription_key}
params = {'visualFeatures': 'Categories,Description,Color'}
data = {'url': url}
response = requests.post(analyze_url, headers=headers,
                         params=params, json=data)
response.raise_for_status()

# The 'analysis' object contains various fields that describe the image. The most
# relevant caption for the image is obtained from the 'description' property.
analysis = response.json()
print(json.dumps(response.json()))
ok = json.dumps(response.json())

image_caption = json.loads(ok)["description"]["captions"][0]["text"].capitalize()

# Display the image and overlay it with the caption.
image = Image.open(BytesIO(requests.get(url).content))
plt.imshow(image)
plt.axis("off")
_ = plt.title(image_caption, size="x-large", y=-0.1)
plt.show()