import requests
from dotenv import load_dotenv
import os

from app.utils.utils import write_json, read_json

load_dotenv()

def create_user():
    USER_URL = "https://www.abibliadigital.com.br/api/users"

    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    body = {
        "name": "Tafnes",
        "email": "tafnessilvabarbosa@gmail.com",
        "password": "123456789", # minimum size 6 digits
        "notifications": False # receive update emails from www.abibliadigital.com.br
    }

    response = requests.post(USER_URL, headers=headers, json=body)
    user_content = response.json()
    return user_content

def get_token():
    USER_URL = f"https://www.abibliadigital.com.br/api/users/token"

    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    body = {
        "email": "tafnessilvabarbosa@gmail.com",
        "password": "123456789", # minimum size 6 digits
    }

    response = requests.put(USER_URL, headers=headers, json=body)
    user_content = response.json()
    return user_content

def get_credentials():
    token = os.getenv("BIBLIA_KEY")
    if not token:
        user_content = create_user()
        if 'token' not in user_content.keys():
            user_content = get_token()
        token = user_content['token']
        with open('.env', 'w') as file:
            file.write(f'BIBLIA_KEY="{token}"')
    return token

def get_verse(book, chapter, verse):
    token = get_credentials()

    books = get_books()

    VERSO_URL = f"https://www.abibliadigital.com.br/api/verses/acf/{books[book]}/{chapter}/{verse}"

    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(VERSO_URL, headers=headers)
    user_content = response.json()

def get_versions():
    token = get_credentials()

    VERSAO_URL = "https://www.abibliadigital.com.br/api/versions"

    headers = { 
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(VERSAO_URL, headers=headers)
    user_content = response.json()
    pass

def get_books():
    books_path = 'app/biblia_api/books.json'
    if not os.path.exists(books_path):
        token = get_credentials()

        LIVROS_URL = "https://www.abibliadigital.com.br/api/books"

        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(LIVROS_URL, headers=headers)
        user_content = response.json()
        books = {}
        for item in user_content:
            books[item['name']] = item['abbrev']['pt']

        write_json(books, books_path)
    else:
        books = read_json(books_path)
    return books