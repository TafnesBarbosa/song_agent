import os

from app.utils.utils import read_song, write_json
from app.agents.agent import verse_picker

def main():
    songs_path = '/home/tafnes/Documentos/Python/Louvor/songlib/songs'
    songs_out_path = 'output'

    # songs_lyric_jsons = []
    for song_file in os.listdir(songs_path):
        song_path = os.path.join(songs_path, song_file)
        lyric_json, song_json = read_song(song_path)
        verses = verse_picker(lyric_json['song'])
        # songs_lyric_jsons.append(lyric_json)
        # songs_lyric.append(lyric)
        song_json['verses'] = verses
        write_json(song_json, os.path.join(songs_out_path, song_file))
    
    # Da um verso similar por IA
    
if __name__ == '__main__':
    # verso = get_verse('1 Timóteo', 3, 16)
    # books = get_books()
    main()