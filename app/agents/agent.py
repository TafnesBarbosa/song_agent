from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
import json

from app.biblia_api.api import get_books, get_verse

PROMPTS_PATH = 'app/agents/prompts'

class GeminiClient:
    client = None
    tools = None
    config = None
    model = 'gemini-2.5-flash'
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

        content = response.text.split("```")[1]

        if content.startswith("json"):
            content = content[len("json"):].strip()

        verses = json.loads(content)
        
        for verse in verses:
            verse['conteudo'] = get_verse(verse['referencia'][0], verse['referencia'][1], verse['referencia'][2])

        verses_sorted = sorted(verses, key=lambda x: x["score"], reverse=True)

        return verses_sorted
    except Exception:
        return ['Erro ao escolher versículos.']