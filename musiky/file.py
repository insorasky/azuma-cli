# Musiky Python Module https://musiky.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Musiky CLI.
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

    NORMAL = 0  # 普通音质
    BETTER = 1  # 较高音质
    HIGH = 2  # 高品音质
    BEST = 3  # 超清音质
    ORIGINAL = 4  # 无损音质

    MP3 = 100  # MP3格式
    FLAC = 101  # FLAC格式

    ID3 = 200  # ID3标签
    VORBIS = 201  # Vorbis标签

    UNKNOWN = -1  # 未知

    def __init__(self, path):
        self.path = os.path.abspath(path)  # 文件绝对路径
        try:
            self.muta_file = MutaFile(self.path)  # mutagen file对象
        except Exception as e:
            raise FileImportException(self.path, e)
        self.mpeg_info = self.muta_file.info  # 音频采样信息
        self.bitrate = self.mpeg_info.bitrate  # 音频比特率
        self.sample_rate = self.mpeg_info.sample_rate  # 音频采样率
        self.size = os.path.getsize(self.path)  # 文件大小

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
        elif self.muta_file.__class__.__name__ == 'FLAC' or self.muta_file.__class__.__name__ == 'OggFileType':  # Vorbis格式，适用于flac和ogg
            return AudioFile.VORBIS, '0'
        else:  # 未知格式
            return AudioFile.UNKNOWN, '0'

    @property
    def quality(self):
        """音频质量分级
        """
        if 0 < self.bitrate <= 128000:
            return AudioFile.NORMAL  # 普通音质
        elif self.bitrate <= 192000:
            return AudioFile.BETTER  # 较高音质
        elif self.bitrate <= 320000:
            return AudioFile.HIGH  # 高品音质
        elif self.file_type == 'mp3':
            return AudioFile.BEST  # 超清音质
        else:
            return AudioFile.ORIGINAL  # 无损音质
