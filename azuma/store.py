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
import shutil
import time
import logging
import hashlib
import json
from typing import Union

from azuma.exception import InvalidStoreException, FileOrDirectoryExistsException, HeaderProtectedException, \
    HeaderNotFoundException
from azuma.file import AudioFile
from azuma.music import Music, MusicInfo, MusicFileList
from azuma.lyric import Lyric
from azuma.temp import Temp
from azuma.uuid import UUID16
from azuma.audio import convert

HEADERS_PROTECTED = ['id', 'version']


class Edit:
    ADD = 0
    REMOVE = 1

    def __init__(self, type_: int, data: Union[Music, UUID16]):
        self.type = type_
        self.data = data


class Store:
    def __init__(self, path: str):
        self.__path = os.path.abspath(path)
        self.__headers = {}
        self.__musics = []
        self.__edits: list[Edit] = []
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
                    self.__headers[key.strip()] = value.strip()
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
        if store_text:
            song_texts = store_text.split('\n\n')
            for text in song_texts:
                temp = Music()
                temp.info = MusicInfo()
                temp.files = MusicFileList()
                lines = text.split('\n')
                for line in lines:
                    if line == '':
                        continue
                    key, value = re.match(r'(.*?):(.*)', line).groups()
                    if key == 'id':
                        temp.info.id = value
                        music_path = os.path.join(path, 'music/' + str(temp.info.id))
                    elif key == 'title':
                        temp.info.title = value
                    elif key == 'artist':
                        temp.info.artist = json.loads(value)
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

                        if quality >= AudioFile.NORMAL:
                            temp.files.normal = AudioFile(os.path.join(music_path, 'files/normal.mp3'))
                        if quality >= AudioFile.BETTER:
                            temp.files.better = AudioFile(os.path.join(music_path, 'files/better.mp3'))
                        if quality >= AudioFile.HIGH:
                            temp.files.high = AudioFile(os.path.join(music_path, 'files/high.mp3'))
                        if quality >= AudioFile.BEST:
                            temp.files.best = AudioFile(os.path.join(music_path, 'files/best.mp3'))
                        if quality >= AudioFile.ORIGINAL:
                            temp.files.original = AudioFile(os.path.join(music_path, 'files/original.flac'))

                    elif key == 'lyriclang':
                        temp.lyrics = [Lyric(os.path.join(music_path, f'lyrics/{lang.strip()}.azml')) for lang in
                                       value.split(',') if lang]

                self.__musics.append(temp)

    def add(self, music: Music):
        self.__edits.append(Edit(Edit.ADD, music))

    def remove(self, id: UUID16):
        self.__edits.append(Edit(Edit.REMOVE, id))

    def commit(self):
        # Music
        update_time = None
        if len(self.__edits):
            new_items = []
            old_music_count = len(self.__musics)
            for edit in self.__edits:
                if edit.type == Edit.ADD:
                    music = edit.data
                    logging.debug(f'Processing Music {music.info.title}: {music.info.id}')
                    music_path = os.path.join(self.__path, 'music/' + str(music.info.id))
                    os.mkdir(music_path)
                    os.mkdir(os.path.join(music_path, 'cover'))
                    os.mkdir(os.path.join(music_path, 'files'))
                    os.mkdir(os.path.join(music_path, 'lyrics'))
                    tmp = {'id': music.info.id, 'title': music.info.title}
                    if music.info.artist:
                        tmp['artist'] = json.dumps(music.info.artist)
                    if music.info.album:
                        tmp['album'] = music.info.album
                    if music.info.type is not None:
                        tmp['type'] = str(music.info.type)
                    if music.info.num is not None:
                        tmp['num'] = str(music.info.num)
                    if music.info.description:
                        tmp['description'] = music.info.description
                    if music.info.cover[1]:
                        with open(os.path.join(music_path, 'cover/cover'), 'wb') as f:
                            f.write(music.info.cover[1])
                        tmp['cover'] = 'cover'
                    highest_quality = music.files.highest_quality()
                    for quality in range(AudioFile.NORMAL, highest_quality + 1):
                        if music.files.get_file_from_quality(quality) is None:
                            if quality < highest_quality:
                                output_path = os.path.join(music_path,
                                                           f'files/{AudioFile.get_quality_str(quality)}.mp3')
                                convert(
                                    input_file=music.files.get_file_from_quality(highest_quality),
                                    output_path=output_path,
                                    quality=quality
                                )
                                file = open(output_path, 'rb')
                                md5 = hashlib.md5(file.read()).hexdigest()
                                file.close()
                                with open(output_path + '.md5', 'w') as f:
                                    f.write(md5)
                        else:
                            output_path = os.path.join(music_path,
                                                       f'files/{AudioFile.get_quality_str(quality)}{os.path.splitext(music.files.get_file_from_quality(quality).path)[1]}')
                            shutil.copyfile(
                                music.files.get_file_from_quality(quality).path,
                                output_path
                            )
                            file = open(output_path, 'rb')
                            md5 = hashlib.md5(file.read()).hexdigest()
                            file.close()
                            with open(output_path + '.md5', 'w') as f:
                                f.write(md5)
                    tmp['quality'] = AudioFile.get_quality_str(highest_quality)

                    # Lyrics
                    languages = []
                    for lyric in music.lyrics:
                        lyric.export(os.path.join(music_path, f'lyrics/{lyric.lang}.azml'))
                        languages.append(lyric.lang)
                    tmp['lyriclang'] = ','.join(languages)
                    new_items.append(tmp)

                    self.__musics.append(music)
                elif edit.type == Edit.REMOVE:
                    shutil.rmtree(os.path.join(self.__path, 'music/' + str(edit.data)))
                    new_items.append({'remove': str(edit.data)})

            # Write to meta
            update_time = int(time.time() * 1000)
            self.__headers['list'] += ',' + str(update_time)

            with lzma.open(os.path.join(self.__path, 'meta/list/all.xz'), 'r') as f:
                data = f.read().decode('utf-8')
            with lzma.open(os.path.join(self.__path, 'meta/list/all.xz'), 'w') as f:
                if data:
                    blocks = data.split('\n\n')
                    if blocks[-1] == '':
                        blocks.pop()
                    removed_identities = ['id:' + str(item.data) for item in self.__edits if item.type == Edit.REMOVE]
                    blocks = [block for block in blocks if block.split('\n')[0] not in removed_identities]
                    data = '\n\n'.join(blocks)
                data += (''.join([
                            (('\n' if (i or old_music_count) else '') + '\n'.join([f'{key}:{value}' for key, value in info.items()]) + '\n')
                            for i, info in enumerate(new_items) if 'remove' not in info
                        ]))
                f.write(data.encode('utf-8'))

            with lzma.open(os.path.join(self.__path, f'meta/list/{update_time}.xz'), 'w') as f:
                f.write(
                    ('\n'.join([
                        '\n'.join([f'{key}:{value}' for key, value in info.items()])
                        for info in new_items
                    ])
                     + '\n').encode('utf-8')
                )

        # Headers
        if update_time is None:
            update_time = int(time.time() * 1000)
        self.__headers['last_update'] = str(update_time)
        header_text = '\n'.join([f'{key}:{value}' for key, value in self.__headers.items()])
        with lzma.open(os.path.join(self.__path, 'meta/header.xz'), 'w') as f:
            f.write(header_text.encode('utf-8'))

        self.__edits = []

    def set_header(self, key: str, value: str):
        if key in HEADERS_PROTECTED:
            raise HeaderProtectedException(key)
        self.__headers[key] = value

    def remove_header(self, key):
        if key in HEADERS_PROTECTED:
            raise HeaderProtectedException(key)
        if key not in self.__headers:
            raise HeaderNotFoundException(key)
        del self.__headers[key]

    @property
    def id(self):
        return UUID16(self.__headers['id'])

    @property
    def path(self):
        return self.__path

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


def generate_store_from_temp(path: str, temp: Temp):
    pass
