#!/usr/bin/env python3
import requests

url = "http://127.0.0.1:5001/item/locations"

response = requests.get(url, params={'locations': 'kolfe'})
print(response.json())
