# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from pydub import AudioSegment
from azuma.file import AudioFile
from azuma.exception import TargetQualityHigherThanCurrentException, InvalidQualityException
import os


def convert(input_file: AudioFile, output_path: str, quality: int):
    """
    转换文件质量并清除歌曲信息，返回生成文件的AudioFile
    """
    curr = AudioSegment.from_file(input_file.path)
    format = os.path.splitext(output_path)[-1][1:]
    if quality == AudioFile.NORMAL:
        bitrate = '128k'
    elif quality == AudioFile.BETTER:
        bitrate = '192k'
    elif quality == AudioFile.HIGH:
        bitrate = '320k'
    elif quality == AudioFile.BEST:
        bitrate = None
    elif quality == AudioFile.ORIGINAL:
        bitrate = None
    else:
        raise InvalidQualityException(quality)
    curr.export(output_path, format=format, bitrate=bitrate)
    return AudioFile(output_path)
