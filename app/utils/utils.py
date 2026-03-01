import json
import re

def write_json(json_dict, json_path):
    json_object = json.dumps(json_dict, indent = 4, ensure_ascii=False)
    with open(json_path, 'w', encoding='utf-8') as file:
        file.write(json_object)
        file.close()

def read_json(json_path):
    with open(json_path) as file:
        json_file = json.load(file)
    return json_file

def read_song(song_path):
    song_json = read_json(song_path)
    lyric_json = {}
    chord_chart = song_json['chord_chart'].split('\n')
    
    # Escreve a letra em formato json
    bloco = []
    last_bloc = None
    for line_in in chord_chart:
        line = line_in.strip()

        # Verifica se a linha é definição de bloco
        match = re.search(r"\[(.*?)\]", line)
        if match:
            if last_bloc is not None:
                lyric_json[last_bloc] = bloco
            last_bloc = match.group(1)
            lyric_json[match.group(1)] = []
            bloco = []
        else:
            # Verifica se não é linha de acordes
            if not line.startswith('.') and len(line) != 0:
                bloco.append(line)
    
    # Escreve a letra em formato normal
    lyric = []
    for key, bloc in lyric_json.items():
        lyric.append(f'[{key}]')
        for line in bloc:
            lyric.append(line)
        lyric.append('')
    
    return lyric_json, lyric