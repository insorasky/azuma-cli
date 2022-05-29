# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma Repository Manager Module.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

import os
import logging
import argparse
from mimetypes import guess_type

from azuma import convert, AudioFile, Lyric, Store, Music, Repository, generate_repository_from_store, UUID16, exception, \
    __version__

parser = argparse.ArgumentParser(description='Azuma CLI - audio distribution tool', prog='azuma',
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
commands:
  create         create a new store
  add            add audio to store
  remove         remove audio from store
  list           list audio in store
  meta           show meta data of store
  commit         commit store to repository
  version        show version
''')

parser.add_argument('command', metavar='command', type=str, help='command to execute',
                    choices=['create', 'add', 'detail', 'edit', 'remove', 'list', 'configure', 'commit', 'version',
                             'audio', 'lyric']
                    )
parser.add_argument('args', metavar='args', type=str, nargs='*', help='arguments for command')
parser.add_argument('-v', '--verbose', action='repository_true', help='verbose output')
parser.add_argument('--language', type=str, help='language for lyric')
parser.add_argument('--original', type=bool, help='original lyric')


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
        store = Store(args.args[0])
    else:
        store = Store(os.getcwd())
        if args.command == 'add':
            music = Music(args.args[0])
            store.commit_music(music)
            print(music.info.id)
        elif args.command == 'remove':
            store.delete_music(UUID16(args.args[0]))
        elif args.command == 'list':
            print('UUID Title Artist')
            for uuid, title, artist in store.all_items():
                print(str(uuid), title, ','.join(artist))
        elif args.command == 'configure':
            if args.args[0] in ['name', 'maintainer', 'description']:
                store.config(args.args[0], args.args[1])
            else:
                raise ValueError(f'{args.args[0]} is not a valid configuration key')
        elif args.command == 'commit':
            generate_repository_from_store(args.args[0], store)
        elif args.command == 'detail':
            print(f'UUID: {store.id}')
            print(f'Name: {store.name}')
            print(f'Maintainer: {store.maintainer}')
            print(f'Description: {store.description}')
        elif args.command == 'edit':
            music_id, key, value = args.args
            music = store.get_music(UUID16(music_id))
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
            subcommand = args.args[0]
            arg = args.args[1:]
            music = store.get_music(UUID16(arg[0]))
            if subcommand == 'add':
                if subcommand.endswith('.lrc'):
                    if args.language:
                        lyric = Lyric.load_from_lrc(arg[1], args.original, args.language)
                    else:
                        raise ValueError('language is required')
                elif subcommand.endswith('.azml'):
                    lyric = Lyric(arg[0])
                else:
                    raise ValueError(f'Unknown type of lyric file: {arg[0]}')
                music.lyrics.append(lyric)
                store.commit_music(music)
            elif subcommand == 'remove':
                lyrics = [lyric for lyric in music.lyrics if lyric.lang == arg[1]]
                if len(lyrics) == 0:
                    raise ValueError(f'No lyric found for {arg[1]}')
                else:
                    for lyric in lyrics:
                        music.lyrics.remove(lyric)
            elif subcommand == 'list':
                print('Artist', 'Creator', 'Offset', 'Language', 'Original', 'Version')
                for lyric in music.lyrics:
                    print(lyric.artist, lyric.creator, lyric.offset, lyric.lang, lyric.orig, lyric.version)
