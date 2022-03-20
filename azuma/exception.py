# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import os


class AzumaException(Exception):
    def __repr__(self):
        return '<AzumaException: Base exception of Azuma>'


class FileImportException(AzumaException):
    def __init__(self, path, e):
        self.path = os.path.abspath(path)
        self.e = e

    def __repr__(self):
        return f'<FileImportException: Cannot import file {self.path}, {type(self.e)}>'


class UUID16InvalidException(AzumaException):
    def __init__(self, u):
        self.u = u

    def __repr__(self):
        return f'<UUID16InvalidException: Invalid UUID16 {self.u}>'


class UnknownTagTypeException(AzumaException):
    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return '<UnknownTagTypeException: Unknown or unsupported tag type>'


class InvalidLRCLineException(AzumaException):
    def __init__(self, line, file):
        self.line = line
        self.file = file

    def __repr__(self):
        return f'<InvalidLRCLine: Invalid line "{self.line}" in LRC file "{self.file}">'


class InvalidStoreException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<InvalidStoreException: Invalid store "{self.path}">'


class FileOrDirectoryExistsException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<FileOrDirectoryExistsException: File or directory "{self.path}" exists>'


class TargetQualityHigherThanCurrentException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<TargetQualityHigherThanCurrentException: The target quality is higher then current file "{self.path}">'

class InvalidQualityException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<InvalidQualityException: The quality "{self.path}" is invalid>'
