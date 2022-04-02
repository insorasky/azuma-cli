import os
import logging
import argparse
from mimetypes import guess_type

from azuma import convert, AudioFile, Lyric, Temp, Music, Store, generate_store_from_temp, UUID16, exception, __version__

parser = argparse.ArgumentParser(description='Azuma CLI - audio distribution tool', prog='azuma',
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
commands:
  create         create a new temporary
  add            add audio to temporary
  remove         remove audio from temporary
  list           list audio in temporary
  meta           show meta data of temporary
  commit         commit temporary to store
  version        show version
''')

parser.add_argument('command', metavar='command', type=str, help='command to execute',
                    choices=['create', 'add', 'detail', 'edit', 'remove', 'list', 'configure', 'commit', 'version',
                             'audio', 'lyric']
                    )
parser.add_argument('args', metavar='args', type=str, nargs='*', help='arguments for command')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')


def main(args=None):
    args = parser.parse_args(args)

    verbose = args.verbose

    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.command == 'version':
        print(f'Azuma v{__version__}')
    elif args.command == 'create':
        if os.path.exists(args.args[0]):
            raise FileExistsError(f'{args.args[0]} already exists')
        temp = Temp(args.args[0])
    else:
        temp = Temp(os.getcwd())
        if args.command == 'add':
            music = Music(args.args[0])
            temp.commit_music(music)
            print(music.info.id)
        elif args.command == 'remove':
            temp.delete_music(UUID16(args.args[0]))
        elif args.command == 'list':
            print('UUID Title Artist')
            for uuid, title, artist in temp.all_items():
                print(str(uuid), title, ','.join(artist))
        elif args.command == 'configure':
            if args.args[0] in ['name', 'maintainer', 'description']:
                temp.config(args.args[0], args.args[1])
            else:
                raise ValueError(f'{args.args[0]} is not a valid configuration key')
        elif args.command == 'commit':
            generate_store_from_temp(args.args[0], temp)
        elif args.command == 'detail':
            print(f'UUID: {temp.id}')
            print(f'Name: {temp.name}')
            print(f'Maintainer: {temp.maintainer}')
            print(f'Description: {temp.description}')
        elif args.command == 'edit':
            music_id, key, value = args.args
            music = temp.get_music(UUID16(music_id))
            if key in ['title', 'album', 'description']:
                music.info.__dict__[key] = value
            elif key == 'artist':
                music.info.artist = value.split(',')
            elif key == 'cover':
                with open(value, 'rb') as f:
                    music.info.cover = guess_type(value)[0], f.read()
            elif key in ['type', 'num']:
                music.info.__dict__[key] = int(value)
            else:
                raise ValueError(f'{key} is not a valid key')
        elif args.command == 'lyric':
            pass
