import os
import requests

cleanvoice_api_key = os.environ["CLEANVOICE_API_KEY"]

url = 'https://api.cleanvoice.ai/v1/upload?filename=audio.mp3'
headers = {'X-API-Key': cleanvoice_api_key}
response = requests.post(url, headers=headers)
signed_url = response.json()['signedUrl']
print(signed_url)