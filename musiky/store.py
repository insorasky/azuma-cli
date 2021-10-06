# Musiky Python Module https://musiky.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Musiky CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os
import lzma
import re
from musiky.exception import InvalidStoreException
from musiky.music import Music


class Store:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.headers = {}
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
            pass

    def add(self, music: Music):
        pass

    def commit(self):
        pass

    def set_header(self, headers: tuple[str, str]):
        pass

    @staticmethod
    def create():
        pass
