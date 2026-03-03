from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
import json
from google.genai import errors

from app.biblia_api.api import get_books, get_verse

PROMPTS_PATH = 'app/agents/prompts'

class GeminiClient:
    client = None
    tools = None
    config = None
    model = 'gemini-2.5-flash'
    # model = 'gemini-3-flash-preview'
    # model = 'gemini-2.5-pro'
    num_chamadas = 0

    @classmethod
    def get_client(cls, system_instruction=None):
        if cls.client is None:
            cls.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        cls.config = types.GenerateContentConfig(
            system_instruction=system_instruction
        )
        return cls.client

    @classmethod
    def generate_content(cls, contents, model=None, system_instruction=None):
        client = cls.get_client(system_instruction=system_instruction)
        cls.num_chamadas += 1
        return client.models.generate_content(
            model=cls.model if model is None else model,
            contents=contents,
            config=cls.config,
        )
    
def verse_picker(musica: dict):
    parar = False
    try:
        with open(os.path.join(PROMPTS_PATH, 'verse_picker', 'syst_prompt.txt'), encoding='utf-8') as file:
            sys_instr = file.read()

        with open(os.path.join(PROMPTS_PATH, 'verse_picker', 'user_prompt.txt'), encoding='utf-8') as file:
            user_prompt = file.read()

        books = get_books()
        sys_instr = sys_instr.replace('{livros}', f'{", ".join(list(books.keys()))}')

        user_prompt = user_prompt.replace('{musica_replace}', f'{musica}')

        response = GeminiClient.generate_content(
            contents=[user_prompt],
            system_instruction=sys_instr
        )
        # response.raise_for_status()
        
        content = response.text.split("```")[1]

        if content.startswith("json"):
            content = content[len("json"):].strip()

        verses = json.loads(content)
        
        for verse in verses:
            verse['conteudo'] = get_verse(verse['referencia'][0], verse['referencia'][1], verse['referencia'][2])

        verses_sorted = sorted(verses, key=lambda x: x["score"], reverse=True)

        return verses_sorted, parar
    except errors.ClientError as e:
        if e.code == 429:
            print('Atingiu limite diário de requisições')
        return ['Erro ao escolher versículos.'], True
    except Exception as e:
        print(f'Erro: {e}\n')
        return ['Erro ao escolher versículos.'], True
    
def completar_song(song_json, lyric_json):
    not_fixed = 0
    not_fixed_all = 0
    parar = False
    if 'verses' in song_json.keys():
        for verse in song_json['verses']:
            if isinstance(verse, dict):
                if verse['conteudo'] == "Erro ao pegar versículo":
                    verse_right = get_verse(verse['referencia'][0], verse['referencia'][1], verse['referencia'][2])
                    if verse_right == "Erro ao pegar versículo":
                        not_fixed += 1
                    verse['conteudo'] = verse_right
            else:
                if verse == 'Erro ao escolher versículos.':
                    verses, parar = verse_picker(lyric_json['song'])
                    if verses == 'Erro ao escolher versículos.':
                        not_fixed_all += 1
                    song_json['verses'] = verses

        # print(f'Não consertados: {not_fixed} versos dentro; {not_fixed_all} erros de IA')
        return song_json, parar
    else:
        verses, parar = verse_picker(lyric_json['song'])
        song_json['verses'] = verses
        return song_json, parar