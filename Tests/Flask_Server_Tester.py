import requests

url = "http://127.0.0.1:5000/upload"
file_path = "Files/brainrot.pdf"  

with open(file_path, 'rb') as file:
    response = requests.post(url, files={"file": file})

print(response.json())