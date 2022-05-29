# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma Repository Manager Module.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

from .audio import convert
from .file import AudioFile
from .lyric import Lyric
from .store import Store
from .music import Music
from .repository import Repository, generate_repository_from_store
from .uuid import UUID16

__version__ = '1.0'

__all__ = ['convert', 'AudioFile', 'Lyric', 'Store', 'Music', 'Repository', 'generate_repository_from_store', 'UUID16', 'exception']
