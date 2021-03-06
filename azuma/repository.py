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
import lzma
import re
import shutil
import time
import logging
import hashlib
import json
from distutils.version import LooseVersion
from typing import Union

from azuma.exception import InvalidRepositoryException, FileOrDirectoryExistsException, HeaderProtectedException, \
    HeaderNotFoundException, RepositoryIdNotMatchException, RepositoryVersionIncompatibleException, RepositoryLaterThanNowException, \
    RepositoryNotChangedException
from azuma.file import AudioFile
from azuma.music import Music, MusicInfo, MusicFileList
from azuma.lyric import Lyric
from azuma.store import Store
from azuma.uuid import UUID16
from azuma.audio import convert
from azuma.utils import STORE_VERSION

HEADERS_PROTECTED = ['id', 'version']


class Edit:
    ADD = 0
    REMOVE = 1

    def __init__(self, type_: int, data: Union[Music, UUID16]):
        self.type = type_
        self.data = data


class Repository:
    def __init__(self, path: str):
        self.__path = os.path.abspath(path)
        self.__headers = {}
        self.__musics = []
        self.__edits: list[Edit] = []
        self.__header_edited: bool = False
        if not os.path.isdir(path):
            raise InvalidRepositoryException(path)

        # Initialize headers
        header_path = os.path.join(path, 'meta/header.xz')
        if not os.path.exists(header_path):
            raise InvalidRepositoryException(path)
        try:
            with lzma.open(header_path) as f:
                for line in [line.decode('utf-8').strip() for line in f.readlines()]:
                    if line == '':  # Empty line
                        continue
                    key, value = re.match(r'^(.*?):(.*)$', line).groups()
                    key, value = key.strip(), value.strip()
                    if value == '':
                        value = None
                    self.__headers[key] = value
        except (lzma.LZMAError, FileNotFoundError):
            raise InvalidRepositoryException(path)

        # Initialize repository
        repository_text_path = os.path.join(path, 'meta/list/all.xz')
        if not os.path.exists(repository_text_path):
            raise InvalidRepositoryException(path)
        try:
            with lzma.open(repository_text_path) as f:
                repository_text = f.read().decode('utf-8')
        except (lzma.LZMAError, FileNotFoundError):
            raise InvalidRepositoryException(path)
        if repository_text:
            song_texts = repository_text.split('\n\n')
            for text in song_texts:
                store = Music()
                store.info = MusicInfo()
                store.files = MusicFileList()
                lines = text.split('\n')
                for line in lines:
                    cover_mime = None
                    cover = None
                    if line == '':
                        continue
                    key, value = re.match(r'^(.*?):(.*)$', line).groups()
                    if key == 'id':
                        store.info.id = UUID16(value)
                        music_path = os.path.join(path, 'music/' + str(store.info.id))
                    elif key == 'title':
                        store.info.title = value
                    elif key == 'artist':
                        store.info.artist = json.loads(value)
                    elif key == 'album':
                        store.info.album = value
                    elif key == 'type':
                        store.info.type = int(value)
                    elif key == 'num':
                        store.info.num = int(value)
                    elif key == 'description':
                        store.info.description = value
                    elif key == 'cover_mime':
                        cover_mime = value
                    elif key == 'cover':
                        cover = open(os.path.join(music_path, 'cover/' + value), 'rb').read()
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
                            raise InvalidRepositoryException(path)

                        if quality >= AudioFile.NORMAL:
                            store.files.normal = AudioFile(os.path.join(music_path, 'files/normal.mp3'))
                        if quality >= AudioFile.BETTER:
                            store.files.better = AudioFile(os.path.join(music_path, 'files/better.mp3'))
                        if quality >= AudioFile.HIGH:
                            store.files.high = AudioFile(os.path.join(music_path, 'files/high.mp3'))
                        if quality >= AudioFile.BEST:
                            store.files.best = AudioFile(os.path.join(music_path, 'files/best.mp3'))
                        if quality >= AudioFile.ORIGINAL:
                            store.files.original = AudioFile(os.path.join(music_path, 'files/original.flac'))

                    elif key == 'lyriclang':
                        store.lyrics = [Lyric(os.path.join(music_path, f'lyrics/{lang.strip()}.azml')) for lang in
                                       value.split(',') if lang]

                    store.info.cover = (cover_mime, cover)

                self.__musics.append(store)

    def add(self, music: Music):
        self.__edits.append(Edit(Edit.ADD, music))

    def remove(self, music_id: UUID16):
        # for item in self.__edits:
        #     if item.data.info.id == music_id:
        #         self.__edits.remove(item)
        #     if music_id in self.__musics:
        self.__edits.append(Edit(Edit.REMOVE, music_id))

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
                        tmp['cover_mime'] = music.info.cover[0]
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
                    data = '\n\n'.join(blocks).strip()
                data += ('\n\n' + ('\n\n'.join(['\n'.join([f'{key}:{value}' for key, value in info.items()])
                                                for info in new_items if 'remove' not in info])))
                f.write(data.strip().encode('utf-8'))

            with lzma.open(os.path.join(self.__path, f'meta/list/{update_time}.xz'), 'w') as f:
                data = '\n\n'.join(['\n'.join([f'{key}:{value}' for key, value in info.items()])
                                    for info in new_items]).strip()
                f.write(data.encode('utf-8'))

            self.__headers['last_update'] = str(update_time)
        else:  # No edits
            if not self.__header_edited:
                raise RepositoryNotChangedException(self.__path)
            # Write to meta
            # update_time = int(time.time() * 1000)
            # self.__headers['list'] += ',' + str(update_time)
            # with lzma.open(os.path.join(self.__path, f'meta/list/{update_time}.xz'), 'w') as f:
            #     f.write(b'')

        # Headers
        # if update_time is None:
        #     update_time = int(time.time() * 1000)
        header_text = '\n'.join([f'{key}:{value if value else ""}' for key, value in self.__headers.items()])
        with lzma.open(os.path.join(self.__path, 'meta/header.xz'), 'w') as f:
            f.write(header_text.encode('utf-8'))

        self.__edits = []

    def set_header(self, key: str, value: str):
        if key in HEADERS_PROTECTED:
            raise HeaderProtectedException(key)
        try:
            rewrite = self.get_header(key) != value
        except HeaderNotFoundException:
            rewrite = True
        if rewrite:
            self.__headers[key] = value
            self.__header_edited = True

    def remove_header(self, key):
        if key in HEADERS_PROTECTED:
            raise HeaderProtectedException(key)
        if key not in self.__headers:
            raise HeaderNotFoundException(key)
        del self.__headers[key]
        self.__header_edited = True

    def get_header(self, key: str):
        if key not in self.__headers:
            raise HeaderNotFoundException(key)
        result = self.__headers[key]
        if result:
            return result
        else:
            return None

    @property
    def id(self):
        # Get repository ID
        return UUID16(self.__headers['id'])

    @property
    def path(self):
        return self.__path

    @staticmethod
    def create(path, repository_id: UUID16):
        path = os.path.abspath(path)
        if os.path.exists(path):
            raise FileOrDirectoryExistsException(path)
        # Create Empty Repository
        os.mkdir(path)
        os.mkdir(os.path.join(path, 'meta'))
        os.mkdir(os.path.join(path, 'meta/list'))
        os.mkdir(os.path.join(path, 'music'))
        with lzma.open(os.path.join(path, 'meta/header.xz'), 'wb') as f:
            f.write(f'id:{str(repository_id)}\n'
                    f'last_update:0\n'
                    f'version:{STORE_VERSION}\n'
                    f'list:all\n'.encode('UTF-8'))
        with lzma.open(os.path.join(path, 'meta/list/all.xz'), 'wb') as f:
            f.write(''.encode('UTF-8'))
        return Repository(path)

    @property
    def music_id_list(self):
        return [item.info.id for item in self.__musics]


def generate_repository_from_store(path: str, store: Store):
    if os.path.exists(path):
        repository = Repository(path)
        if repository.id != store.id:
            raise RepositoryIdNotMatchException(repository.id, store.id)
        version = repository.get_header('version')
        if LooseVersion(version) > LooseVersion(STORE_VERSION):
            raise RepositoryVersionIncompatibleException(version)
        if int(repository.get_header('last_update')) > int(time.time() * 1000):
            raise RepositoryLaterThanNowException(repository.get_header('last_update'))
    else:
        repository = Repository.create(path, store.id)
    repository.set_header('name', store.name)
    repository.set_header('maintainer', store.maintainer)
    repository.set_header('description', store.description)
    edits_query = store.get_edit_log(int(repository.get_header('last_update')) / 1000)[::-1]
    edits = []
    removed = set()
    for edit_type, uuid in edits_query:
        if uuid in removed:
            continue
        if edit_type == 0:
            edits.append((edit_type, uuid))
        if edit_type == 1:
            removed.add(uuid)
            if uuid in repository.music_id_list:
                edits.append((edit_type, uuid))
    for edit_type, uuid in edits[::-1]:
        if edit_type == 0:  # Add
            music = store.get_music(uuid)
            repository.add(music)
        elif edit_type == 1:  # Delete
            repository.remove(uuid)
    repository.commit()
    return repository
