import os
import json

from app.utils.utils import read_song, write_json
from app.agents.agent import completar_song
from app.biblia_api.api import get_credentials

def main():
    # songs_path = '/home/tafnes/Documentos/Python/Louvor/songlib/songs'
    songs_path = 'C:\\Lucas\\Repos\\pessoal\\github\\songlib\\songs'
    songs_out_path = 'output'
    # songs_path = songs_out_path

    for k, song_file in enumerate(os.listdir(songs_path)):
        if not song_file.lower().endswith('.json'):
            continue
        song_path = os.path.join(songs_path, song_file)
        song_path_out = os.path.join(songs_out_path, song_file)
        if os.path.isfile(song_path) is False:
            continue
        if os.path.exists(song_path_out):
            continue
        try:
            lyric_json, song_json = read_song(song_path)
        except json.JSONDecodeError as e:
            print(f'Ignorando arquivo inválido: {song_file} ({e})')
            continue
        song_json, parar = completar_song(song_json, lyric_json)
        if parar:
            print('Parando')
            break
        write_json(song_json, song_path_out)
        print(k)
    
if __name__ == '__main__':
    get_credentials()
    # song_path = os.path.join('output', '88340.json')
    # lyric_json, song_json = read_song(song_path)
    # song_json = completar_song(song_json, lyric_json)
    main()
    # verse = song_json['verses'][4]
    # get_verse(verse['referencia'][0], verse['referencia'][1], verse['referencia'][2])
    # songs_out_path = 'output'

    # for k, song_file in enumerate(os.listdir(songs_out_path)):
    #     song_path = os.path.join(songs_out_path, song_file)
    #     lyric_json, song_json = read_song(song_path)
    #     for verse in song_json['verses']:
    #         if 'texto' in verse.keys():
    #             del verse['texto']
    #     write_json(song_json, song_path)