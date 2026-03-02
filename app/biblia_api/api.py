import requests
from dotenv import load_dotenv
import os
import unicodedata

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
    try:
        token = get_credentials()

        books = get_books()

        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        verses = verse.split('-')
        verses_out = ''
        if len(verses) > 1:
            for verse_in in range(int(verses[0]), int(verses[1])+1):
                VERSO_URL = f"https://www.abibliadigital.com.br/api/verses/acf/{books[book]}/{chapter}/{verse_in}"
                response = requests.get(VERSO_URL, headers=headers)
                user_content = response.json()
                verses_out += user_content['text'] + ' '
        else:
            VERSO_URL = f"https://www.abibliadigital.com.br/api/verses/acf/{books[book]}/{chapter}/{verses[0]}"
            response = requests.get(VERSO_URL, headers=headers)
            user_content = response.json()
            verses_out += user_content['text'] + ' '
        return verses_out
    except Exception as e:
        print(f'Erro de verso: {e}\n')
        return 'Erro ao pegar versículo'

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

def update_books():
    books_path = 'app/biblia_api/books.json'
    books = read_json(books_path)
    books_updated = {}
    for key in books.keys():
        if 'ª' in key:
            books_updated[key.replace('ª', '')] = books[key]
            books_updated[remover_acentos(key.replace('ª', ''))] = books[key]
            books_updated[key.replace('ª ', '')] = books[key]
            books_updated[remover_acentos(key.replace('ª ', ''))] = books[key]
        if 'º' in key:
            books_updated[key.replace('º', '')] = books[key]
            books_updated[remover_acentos(key.replace('º', ''))] = books[key]
            books_updated[key.replace('º ', '')] = books[key]
            books_updated[remover_acentos(key.replace('º ', ''))] = books[key]
        books_updated[key] = books[key]
        books_updated[remover_acentos(key)] = books[key]
    write_json(books_updated, books_path)

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

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
        update_books()
    else:
        books = read_json(books_path)
    return books