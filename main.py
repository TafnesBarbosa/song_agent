import os

from app.utils.utils import read_song
from app.agents.agent import verse_picker

def main():
    songs_path = '/home/tafnes/Documentos/Python/Louvor/songlib/songs'

    songs_lyric_jsons = []
    songs_lyric = []
    for song_file in os.listdir(songs_path):
        song_path = os.path.join(songs_path, song_file)
        lyric_json, lyric = read_song(song_path)
        verses = verse_picker(lyric_json['song'])
        songs_lyric_jsons.append(lyric_json)
        songs_lyric.append(lyric)
    
    # Da um verso similar por IA
    
if __name__ == '__main__':
    # verso = get_verse('1 Timóteo', 3, 16)
    # books = get_books()
    main()