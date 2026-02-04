from flask_jwt_extended import create_access_token
import requests
import random 

def crear_token(data):
    return create_access_token(identity=data)

def getData():
    personajes = []
    for i in range(5):
        character_id = random.randint(0,10)
        URL = "https://futuramaapi.com/api/characters/{}".format(character_id)
        response = requests.get(URL)
        response = response.json()
        personajes.append(response)

    return personajes