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
from azuma import __version__ as azuma_version


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
    def __init__(self, quality):
        self.quality = quality

    def __repr__(self):
        return f'<InvalidQualityException: The quality "{self.quality}" is invalid>'


class HeaderProtectedException(AzumaException):
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return f'<HeaderProtectedException: The header "{self.key}" is protected and ' \
               f'cannot be changed after initialization>'


class HeaderNotFoundException(AzumaException):
    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return f'<HeaderNotFoundException: The header "{self.key}" is not found>'


class StoreIdNotMatchException(AzumaException):
    def __init__(self, store_id, temp_id):
        self.store_id = store_id
        self.temp_id = temp_id

    def __repr__(self):
        return f'<StoreIdNotMatchException: The store id "{self.store_id}" does not match the temp id "{self.temp_id}">'


class StoreVersionIncompatibleException(AzumaException):
    def __init__(self, store_version):
        self.store_version = store_version

    def __repr__(self):
        return f'<StoreVersionIncompatibleException: The store version "{self.store_version}" is newer than' \
               f'the current azuma-cli version "{azuma_version}">'
