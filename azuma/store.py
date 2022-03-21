# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma Store Manager Module.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import lzma
import re
import time

from azuma.exception import InvalidStoreException, FileOrDirectoryExistsException
from azuma.file import AudioFile
from azuma.music import Music, MusicInfo, MusicFileList
from azuma.lyric import Lyric
from azuma.temp import Temp
from azuma.uuid import UUID16


class Store:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.headers = {}
        self.musics = []
        if not os.path.isdir(path):
            raise InvalidStoreException(path)

        # Initialize headers
        header_path = os.path.join(path, 'meta/header.xz')
        if not os.path.exists(header_path):
            raise InvalidStoreException(path)
        try:
            with lzma.open(header_path) as f:
                for line in [line.decode('utf-8').strip() for line in f.readlines()]:
                    if line == '':  # Empty line
                        continue
                    key, value = re.match(r'(.*):(.*)', line).groups()
                    self.headers[key.strip()] = value.strip()
                    if key == 'id':
                        self.__id = value
        except (lzma.LZMAError, FileNotFoundError):
            raise InvalidStoreException(path)

        # Initialize store
        store_text_path = os.path.join(path, 'meta/list/all.xz')
        if not os.path.exists(store_text_path):
            raise InvalidStoreException(path)
        try:
            with lzma.open(store_text_path) as f:
                store_text = f.read().decode('utf-8')
        except (lzma.LZMAError, FileNotFoundError):
            raise InvalidStoreException(path)
        song_texts = store_text.split('\n\n')
        for text in song_texts:
            lines = text.split('\n')
            for line in lines:
                if line == '':
                    continue
                key, value = re.match(r'(.*):(.*)', line).groups()
                temp = Music()
                temp.info = MusicInfo()
                temp.files = MusicFileList()
                if key == 'id':
                    temp.info.id = value
                    music_path = os.path.join(path, 'music/' + str(temp.info.id))
                elif key == 'title':
                    temp.info.title = value
                elif key == 'artist':
                    temp.info.artist = value
                elif key == 'album':
                    temp.info.album = value
                elif key == 'type':
                    temp.info.type = int(value)
                elif key == 'num':
                    temp.info.num = int(value)
                elif key == 'description':
                    temp.info.description = value
                elif key == 'cover':
                    temp.info.cover = open(os.path.join(music_path, 'cover/' + value))
                elif key == 'quality':
                    if value == 'normal':
                        quality = AudioFile.NORMAL
                    elif value == 'better':
                        quality = AudioFile.BETTER
                    elif value == 'high':
                        quality = AudioFile.HIGH
                    elif value == 'best':
                        quality = AudioFile.BEST
                    elif value == 'original':
                        quality = AudioFile.ORIGINAL
                    else:
                        raise InvalidStoreException(path)

                    if quality <= AudioFile.NORMAL:
                        temp.files.normal = AudioFile(os.path.join(music_path, 'files/normal.mp3'))
                    elif quality <= AudioFile.BETTER:
                        temp.files.better = AudioFile(os.path.join(music_path, 'files/better.mp3'))
                    elif quality <= AudioFile.HIGH:
                        temp.files.high = AudioFile(os.path.join(music_path, 'files/high.mp3'))
                    elif quality <= AudioFile.BEST:
                        temp.files.best = AudioFile(os.path.join(music_path, 'files/best.mp3'))
                    elif quality <= AudioFile.ORIGINAL:
                        temp.files.original = AudioFile(os.path.join(music_path, 'files/original.flac'))

                elif key == 'lyriclang':
                    temp.lyrics = [Lyric(os.path.join(music_path, f'files/{lang.strip()}.azml')) for lang in value.split(',') if lang]

                self.musics.append(temp)

        self.edits: list[Music] = []

    def add(self, music: Music):
        self.edits.append(music)

    def commit(self):
        update_time = int(time.time() * 1000)
        self.set_header('last_update', update_time)
        header_text = ''
        for key, value in enumerate(self.headers):
            header_text += f'{key}:{value}\n'
        with lzma.open(os.path.join(self.path, 'meta/header.xz'), 'w') as f:
            f.write(header_text.encode('utf-8'))

    def set_header(self, key, value):
        self.headers[str(key)] = str(value)

    @property
    def id(self):
        return UUID16(self.headers['id'])

    @staticmethod
    def create(path, store_id: UUID16):
        path = os.path.abspath(path)
        if os.path.exists(path):
            raise FileOrDirectoryExistsException(path)
        # Create Empty Store
        os.mkdir(path)
        os.mkdir(os.path.join(path, 'meta'))
        os.mkdir(os.path.join(path, 'meta/list'))
        os.mkdir(os.path.join(path, 'music'))
        with lzma.open(os.path.join(path, 'meta/header.xz'), 'wb') as f:
            f.write(f'id:{str(store_id)}\n'
                    f'last_update:{int(time.time() * 1000)}\n'
                    f'version:1.0\n'
                    f'list:all\n'.encode('UTF-8'))
        with lzma.open(os.path.join(path, 'meta/list/all.xz'), 'wb') as f:
            f.write(''.encode('UTF-8'))
        return Store(path)


def generate_store(path: str, temp: Temp):
    pass
