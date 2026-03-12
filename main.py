import os

from app.utils.utils import read_song, write_json, write_songs_text
from app.agents.agent import completar_song, song_picker
from app.biblia_api.api import get_credentials

def main():
    songs_path = '/home/tafnes/Documentos/Python/Louvor/songlib/songs'
    songs_out_path = 'output'
    # songs_path = songs_out_path

    for k, song_file in enumerate(os.listdir(songs_path)):
        song_path = os.path.join(songs_path, song_file)
        song_path_out = os.path.join(songs_out_path, song_file)
        if not os.path.exists(song_path_out):
            lyric_json, song_json = read_song(song_path)
            song_json, parar = completar_song(song_json, lyric_json)
            if parar:
                print('Parando')
                break
            write_json(song_json, song_path_out)
        else:
            lyric_json, song_json = read_song(song_path_out)
            song_json, parar = completar_song(song_json, lyric_json)
            if parar:
                print('Parando')
                break
            write_json(song_json, song_path_out)
        print(k)
    
if __name__ == '__main__':
    # get_credentials()
    # song_path = os.path.join('output', '88340.json')
    # lyric_json, song_json = read_song(song_path)
    # song_json = completar_song(song_json, lyric_json)
    # main()
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
    # write_songs_text('/home/tafnes/Documentos/Python/Louvor/songlib/songs')
    response, parar = song_picker("""Ora, quando cheguei a Trôade para pregar o evangelho de Cristo, e uma porta se me abriu no Senhor, não tive, contudo, tranquilidade no meu espírito, porque não encontrei o meu irmão Tito; por isso, despedindo-me deles, parti para a  Macedônia. Graças, porém, a Deus, que, em Cristo, sempre nos conduz em triunfo e, por meio de nós, manifesta em todo lugar a fragrância do seu conhecimento. Porque nós somos para com Deus o bom perfume de Cristo, tanto nos que são salvos como nos que se perdem. Para com estes, cheiro de morte para morte; para com aqueles, aroma de vida para vida. Quem, porém, é suficiente para estas coisas? Porque nós não estamos, como tantos outros, mercadejando a palavra de Deus; antes, em Cristo é que falamos na presença de Deus, com sinceridade e da parte do próprio Deus.""")
    print(response)