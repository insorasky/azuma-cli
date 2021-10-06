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


class MusikyException(Exception):
    def __repr__(self):
        return '<MusikyException: Base exception of Musiky>'


class FileImportException(MusikyException):
    def __init__(self, path, e):
        self.path = os.path.abspath(path)
        self.e = e

    def __repr__(self):
        return f'<FileImportException: Cannot import file {self.path}, {type(self.e)}>'


class UUID16InvalidException(MusikyException):
    def __init__(self, u):
        self.u = u

    def __repr__(self):
        return f'<UUID16InvalidException: Invalid UUID16 {self.u}>'


class UnknownTagTypeException(MusikyException):
    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return '<UnknownTagTypeException: Unknown or unsupported tag type>'


class InvalidLRCLineException(MusikyException):
    def __init__(self, line, file):
        self.line = line
        self.file = file

    def __repr__(self):
        return f'<InvalidLRCLine: Invalid line "{self.line}" in LRC file "{self.file}">'


class InvalidStoreException(MusikyException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<InvalidStoreException: Invalid store "{self.path}">'
