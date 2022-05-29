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
from azuma.utils import STORE_VERSION


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


class InvalidRepositoryException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<InvalidRepositoryException: Invalid repository "{self.path}">'


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


class RepositoryIdNotMatchException(AzumaException):
    def __init__(self, repository_id, store_id):
        self.repository_id = repository_id
        self.store_id = store_id

    def __repr__(self):
        return f'<RepositoryIdNotMatchException: The repository id "{self.repository_id}" does not match the store id "{self.store_id}">'


class RepositoryVersionIncompatibleException(AzumaException):
    def __init__(self, repository_version):
        self.repository_version = repository_version

    def __repr__(self):
        return f'<RepositoryVersionIncompatibleException: The repository version "{self.repository_version}" is newer than' \
               f'the current azuma-cli version "{STORE_VERSION}">'


class RepositoryLaterThanNowException(AzumaException):
    def __init__(self, last_update):
        self.last_update = last_update

    def __repr__(self):
        return f'<RepositoryVersionIncompatibleException: The repository last update time "{self.last_update}" is later than' \
               f'the current system time>'


class InvalidStoreException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<InvalidStoreException: The store "{self.path}" is invalid>'


class RepositoryNotChangedException(AzumaException):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return f'<RepositoryNotChangedException: The repository "{self.path}" is not changed>'
