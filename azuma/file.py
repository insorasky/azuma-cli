# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from mutagen import File as MutaFile
from .exception import FileImportException
import os


class AudioFile:
    """音频文件对象
    """

    NORMAL = 0  # Normal quality
    BETTER = 1  # Better quality
    HIGH = 2  # High quality
    BEST = 3  # Best quality
    ORIGINAL = 4  # Original quality

    MP3 = 100  # MP3 format
    FLAC = 101  # FLAC format

    ID3 = 200  # ID3 tag
    VORBIS = 201  # Vorbis tag

    UNKNOWN = -1  # Unknown

    def __init__(self, path):
        self.path = os.path.abspath(path)  # Absolute path of the file
        try:
            self.muta_file = MutaFile(self.path)  # Mutagen file object
        except Exception as e:
            raise FileImportException(self.path, e)
        self.mpeg_info = self.muta_file.info  # 音频采样信息
        self.bitrate = self.mpeg_info.bitrate  # Bit rate
        self.sample_rate = self.mpeg_info.sample_rate  # Sample rate
        self.size = os.path.getsize(self.path)  # File sizq

    @property
    def file_type(self):
        """文件类型
        """
        if 'audio/mp3' in self.muta_file.mime:  # MP3
            return AudioFile.MP3
        elif 'audio/flac' in self.muta_file.mime:  # FLAC
            return AudioFile.FLAC
        else:
            return AudioFile.UNKNOWN

    @property
    def meta_type(self):
        """标签类型
        """
        if hasattr(self.muta_file, 'ID3'):  # ID3格式
            return AudioFile.ID3, '.'.join([str(i) for i in self.muta_file.tags.version])
        elif self.muta_file.__class__.__name__ == 'FLAC' or self.muta_file.__class__.__name__ == 'OggFileType':  # Vorbis format (flac and ogg)
            return AudioFile.VORBIS, '0'
        else:  # 未知格式
            return AudioFile.UNKNOWN, '0'

    @property
    def quality(self):
        """音频质量分级
        """
        if 0 < self.bitrate <= 128000:
            return AudioFile.NORMAL
        elif self.bitrate <= 192000:
            return AudioFile.BETTER
        elif self.bitrate <= 320000:
            return AudioFile.HIGH
        elif self.file_type == 'mp3':
            return AudioFile.BEST
        else:
            return AudioFile.ORIGINAL
