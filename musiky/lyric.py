# Musiky Python Module https://musiky.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Musiky CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import re
import os
import json
import lzma
from musiky.exception import InvalidLRCLineException


class Lyric:
    def __init__(self, path: str = None):
        self.artist: str = None  # Lyrics artist
        self.creator: str = None  # Lyrics text creator
        self.offset: int = 0  # Timestamp adjustment in milliseconds
        self.orig: bool = None  # Original lyrics or translated lyrics
        self.lang: str = None  # Lyrics language (RFC4646)
        self.path: str = None  # Full path of lyrics file
        # RFC4646: https://www.ietf.org/rfc/rfc4646.txt
        # ONLY THE PARTS OF language[-region]
        # eg. zh-CN(Simplified Chinese in China Mainland)
        #     zh-HK(Traditional Chinese in Hong Kong)
        #     zh-TW(Traditional Chinese in Taiwan)
        #     zh(Will be shown if no region is specified)
        #     en-US(American English)
        #     en-UK(British English)
        #     en(Will be shown if no region is specified)
        #     ja(Japanese)
        #     fr(French)

        self.lyrics: list[tuple[str, str]] = []  # Time tags(mm:ss.xx), lyric words
        self.version: int = None  # Lyrics version

        if path is not None:
            self.path = os.path.abspath(path)
            with lzma.open(self.path, 'r') as f:
                data = json.loads(f.read())
                self.artist = data['artist']
                self.creator = data['creator']
                self.offset = data['offset']
                self.orig = data['orig']
                self.lang = data['lang']
                self.version = data['version']
                self.lyrics = [(line['time'], line['word']) for line in data['lyrics']]

    def export(self, path: str):
        """
        Export to lyrics LZMA extracted JSON file.
        Extension name should be ".mklrc".
        """
        path = os.path.abspath(path)
        with lzma.open(path, 'w') as f:
            f.write(json.dumps({
                'artist': self.artist,
                'creator': self.creator,
                'offset': self.offset,
                'orig': self.orig,
                'lang': self.lang,
                'version': self.version,
                'lyrics': [{
                    'time': lyric[0],
                    'word': lyric[1]
                } for lyric in self.lyrics]
            }).encode())
        self.path = path

    @staticmethod
    def load_from_lrc(path: str, orig: bool, lang: str = None):
        """
        Currently Musiky lyrics format is not compatible with Enhanced LRC format.
        All extended features (eg. word time tag) will be ignored.
        """
        tmp = Lyric()
        tmp.orig = orig
        tmp.lang = lang
        tmp.version = 1
        with open(path, 'r') as f:
            for line in [line.strip() for line in f.readlines()]:
                data = re.match(r'\[(\d*:\d*\.\d*)](.*)', line)  # Lyric text
                if data is None:
                    if line[-1] == ']':  # ID tag
                        key, value = re.match(r'\[(.*):(.*)]', line).groups()
                        key = key.strip()
                        value = value.strip()
                        if key == 'ar':
                            tmp.artist = value
                        elif key == 'au':
                            tmp.creator = value
                        elif key == 'by':
                            tmp.creator = value
                        elif key == 'offset':
                            tmp.offset = int(value)
                    elif line == '':  # Empty line
                        continue
                    else:  # Invalid line
                        raise InvalidLRCLineException(line, path)
                else:
                    tmp.lyrics.append(tuple(data.groups()))

        return tmp
