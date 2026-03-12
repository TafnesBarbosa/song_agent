from google import genai
from google.genai import types
import os
import time
from dotenv import load_dotenv
load_dotenv()
import json
from google.genai import errors

from app.biblia_api.api import get_books, get_verse

PROMPTS_PATH = 'app/agents/prompts'

# Lista oficial de tags (50), exatamente como no prompt de metadados
TAGS_OFICIAIS = frozenset({
    'soberania', 'santidade', 'criador', 'fidelidade', 'amor', 'poder', 'cruz', 'ressurreição',
    'redentor', 'rei', 'cordeiro', 'Espírito', 'presença', 'salvação', 'graça', 'arrependimento',
    'perdão', 'justificação', 'fé', 'confiança', 'esperança', 'santificação', 'redenção', 'misericórdia', 'glória',
    'abertura', 'chamado', 'adoração', 'confissão', 'resposta', 'apelo', 'ceia', 'oferta', 'encerramento', 'oração',
    'páscoa', 'natal', 'pentecostes', 'aninho', 'gratidão', 'missões', 'família', 'jovens', 'retiro', 'conferência',
    'celebrativo', 'contemplativo', 'intenso', 'solene', 'alegre'
})

class GeminiClient:
    client = None
    tools = None
    config = None

    model = 'gemini-3.1-flash-lite-preview'
    # model = 'gemini-2.5-flash'
    # model = 'gemini-2.5-flash-lite'

    # model = 'gemini-2.0-flash'
    # model = 'gemini-2.0-flash-lite'
    # model = 'gemini-flash-lite-latest'
    # model = 'gemini-flash-latest'
    # model = 'gemini-3-flash-preview'


    num_chamadas = 0
    # Limite de requisições por minuto (pode ser ajustado via variável de ambiente GEMINI_MAX_RPM)
    max_rpm = int(os.getenv("GEMINI_MAX_RPM", "60"))
    last_request_ts = None

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

        # Controle simples de RPM (requisições por minuto)
        if cls.max_rpm and cls.max_rpm > 0:
            min_interval = 60.0 / cls.max_rpm
            now = time.time()
            if cls.last_request_ts is not None:
                elapsed = now - cls.last_request_ts
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)
                    now = time.time()
            cls.last_request_ts = now

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


def _extract_json_from_response(text: str) -> dict:
    """Extrai JSON do texto de resposta (suporta bloco ```json ou JSON puro)."""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts[1:]:
            part = part.strip()
            if part.lower().startswith("json"):
                part = part[4:].strip()
            try:
                return json.loads(part)
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Nenhum JSON válido encontrado na resposta")


def _apply_metadata_from_dict(song_json, data):
    """Aplica time_sig, tempo, feel e tags vindos de um dicionário de metadados."""
    if data.get('time_sig') is not None and not (song_json.get('time_sig') or '').strip():
        song_json['time_sig'] = str(data['time_sig']).strip()
    if data.get('tempo') is not None and (song_json.get('tempo') in (None, '', 0) or not str(song_json.get('tempo') or '').strip()):
        song_json['tempo'] = int(data['tempo']) if data['tempo'] != '' else ''
    if data.get('feel') is not None and not (song_json.get('feel') or '').strip():
        song_json['feel'] = str(data['feel']).strip()
    if data.get('tags') is not None and (not song_json.get('tags') or (isinstance(song_json.get('tags'), str) and not str(song_json.get('tags')).strip())):
        raw = data['tags']
        if not isinstance(raw, list):
            raw = [raw] if raw else []
        # Aceita só tags da lista oficial (normaliza minúscula para comparação; mantém "Espírito" se vier assim)
        valid = []
        lower_set = {x.lower() for x in TAGS_OFICIAIS}
        for t in raw:
            s = str(t).strip()
            if not s:
                continue
            s_lower = s.lower()
            if s_lower in lower_set:
                oficial = next(x for x in TAGS_OFICIAIS if x.lower() == s_lower)
                if oficial not in valid:
                    valid.append(oficial)
        song_json['tags'] = valid[:5] if len(valid) >= 5 else valid


def full_song_analysis(song_json, lyric_json):
    """Chama a IA UMA vez para obter versos + metadados da música."""
    parar = False
    try:
        with open(os.path.join(PROMPTS_PATH, 'song_full', 'syst_prompt.txt'), encoding='utf-8') as file:
            sys_instr = file.read()
        with open(os.path.join(PROMPTS_PATH, 'song_full', 'user_prompt.txt'), encoding='utf-8') as file:
            user_prompt = file.read()

        musica_input = {
            'titulo': lyric_json['song']['titulo'],
            'letra': lyric_json['song']['letra'],
            'chord_chart': song_json.get('chord_chart', '') or ''
        }
        user_prompt = user_prompt.replace('{musica_replace}', json.dumps(musica_input, ensure_ascii=False))

        response = GeminiClient.generate_content(
            contents=[user_prompt],
            system_instruction=sys_instr
        )
        data = _extract_json_from_response(response.text)

        # Versículos
        verses = data.get('verses', [])
        if isinstance(verses, list):
            for verse in verses:
                if isinstance(verse, dict) and 'referencia' in verse:
                    ref = verse['referencia']
                    if isinstance(ref, list) and len(ref) == 3:
                        verse['conteudo'] = get_verse(ref[0], ref[1], ref[2])
        song_json['verses'] = sorted(
            verses,
            key=lambda x: x.get("score", 0),
            reverse=True,
        ) if isinstance(verses, list) else verses

        # Metadados
        metadata = data.get('metadata', {}) or {}
        if isinstance(metadata, dict):
            _apply_metadata_from_dict(song_json, metadata)

        return song_json, parar
    except errors.ClientError as e:
        if e.code == 429:
            print('Atingiu limite diário de requisições (full_song_analysis)')
        return song_json, True
    except Exception as e:
        print(f'Erro em full_song_analysis: {e}\n')
        return song_json, True


def fill_song_metadata(song_json, lyric_json):
    """Preenche time_sig, tempo, feel e tags na música usando IA quando estiverem vazios."""
    need_fill = (
        not (song_json.get('time_sig') or '').strip() or
        (song_json.get('tempo') in (None, '', 0) or not str(song_json.get('tempo') or '').strip()) or
        not (song_json.get('feel') or '').strip() or
        not song_json.get('tags') or (isinstance(song_json.get('tags'), str) and not song_json.get('tags').strip())
    )
    if not need_fill:
        return
    try:
        with open(os.path.join(PROMPTS_PATH, 'song_metadata', 'syst_prompt.txt'), encoding='utf-8') as file:
            sys_instr = file.read()
        with open(os.path.join(PROMPTS_PATH, 'song_metadata', 'user_prompt.txt'), encoding='utf-8') as file:
            user_prompt = file.read()

        musica_input = {
            'titulo': lyric_json['song']['titulo'],
            'letra': lyric_json['song']['letra'],
            'chord_chart': song_json.get('chord_chart', '') or ''
        }
        user_prompt = user_prompt.replace('{musica_replace}', json.dumps(musica_input, ensure_ascii=False))

        response = GeminiClient.generate_content(
            contents=[user_prompt],
            system_instruction=sys_instr
        )
        data = _extract_json_from_response(response.text)
        _apply_metadata_from_dict(song_json, data)
    except errors.ClientError as e:
        if e.code == 429:
            print('Atingiu limite diário de requisições (metadados)')
    except Exception as e:
        print(f'Erro ao preencher metadados: {e}\n')


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
        fill_song_metadata(song_json, lyric_json)
        return song_json, parar
    else:
        # Para músicas novas (sem verses), faz tudo em UMA chamada de IA
        song_json, parar = full_song_analysis(song_json, lyric_json)
        return song_json, parar