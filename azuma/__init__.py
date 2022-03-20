# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma Store Manager Module.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from .audio import convert
from .file import AudioFile
from .lyric import Lyric
from .temp import Temp
from .music import Music
from .store import Store, generate_store
from .uuid import UUID16

__version__ = '0.0.1'

__all__ = ['convert', 'AudioFile', 'Lyric', 'Temp', 'Music', 'Store', 'generate_store', 'UUID16', 'exception']
