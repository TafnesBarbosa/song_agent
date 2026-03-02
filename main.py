import os

from app.utils.utils import read_song, write_json
from app.agents.agent import completar_song
from app.biblia_api.api import get_verse

def main():
    songs_path = '/home/tafnes/Documentos/Python/Louvor/songlib/songs'
    songs_out_path = 'output'

    for k, song_file in enumerate(os.listdir(songs_out_path)):
        song_path = os.path.join(songs_out_path, song_file)
        lyric_json, song_json = read_song(song_path)
        # verses = verse_picker(lyric_json['song'])
        # song_json['verses'] = verses
        song_json = completar_song(song_json, lyric_json)
        write_json(song_json, os.path.join(songs_out_path, song_file))
        print(k)
    
if __name__ == '__main__':
    # song_path = os.path.join('output', '88340.json')
    # lyric_json, song_json = read_song(song_path)
    # song_json = completar_song(song_json, lyric_json)
    main()
    # verse = song_json['verses'][4]
    # get_verse(verse['referencia'][0], verse['referencia'][1], verse['referencia'][2])