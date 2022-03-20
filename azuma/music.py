# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from azuma.uuid import UUID16
from azuma.file import AudioFile
from azuma.exception import UnknownTagTypeException
from azuma.lyric import Lyric


class MusicInfo:
    """单曲信息对象
    """
    def __init__(self):
        """初始化MusicInfo对象
        """
        self.id: UUID16 = None  # 曲目ID
        self.title: str = None  # 曲名
        self.artist: str = None  # 艺术家
        self.album: str = None  # 专辑
        self.cover: tuple[str, bytes] = None, None  # 专辑封面(MIME, 封面内容)
        self.type: int = None  # 歌曲类型
        self.num: int = None  # 歌曲在专辑内的位置
        self.description: str = None  # 备注

    @staticmethod
    def load_from_file(file: AudioFile):
        """从AudioFile对象对应的文件载入单曲信息并导入新的MusicInfo对象
        """
        tmp = MusicInfo()
        m = file.muta_file
        t, v = file.meta_type
        if t == AudioFile.ID3:
            try:
                tmp.title = m['TIT2'].text[0]
            except (KeyError, IndexError):
                pass
            try:
                tmp.artist = m['TPE1'].text
            except (KeyError, IndexError):
                pass
            try:
                tmp.album = m['TALB'].text[0]
            except (KeyError, IndexError):
                pass
            try:
                tmp.cover = m['APIC:'].mime, m['APIC:'].data
            except (KeyError, IndexError):
                pass
            try:
                tmp.type = m['TCON'].text[0]
            except (KeyError, IndexError):
                pass
            try:
                tmp.num = int(m['TRCK'].text[0])
            except (KeyError, IndexError):
                pass
        elif t == AudioFile.VORBIS:
            try:
                tmp.title = m['title'][0]
            except (KeyError, IndexError):
                pass
            try:
                tmp.artist = m['artist']
            except (KeyError, IndexError):
                pass
            try:
                tmp.album = m['album'][0]
            except (KeyError, IndexError):
                pass
            try:
                tmp.cover = m.pictures[0].mime, m.pictures[0].data
            except (KeyError, IndexError):
                pass
            try:
                tmp.type = m['genre'][0]
            except (KeyError, IndexError):
                pass
            try:
                tmp.num = int(m['tracknumber'][0])
            except (KeyError, IndexError):
                pass
        else:
            raise UnknownTagTypeException(m.__class__.__name__)
        return tmp


class MusicFileList:
    """单曲音频文件列表
    """
    def __init__(self):
        self.normal: AudioFile = None  # 普通音质
        self.better: AudioFile = None  # 较高音质
        self.high: AudioFile = None  # 高品音质
        self.best: AudioFile = None  # 超清音质
        self.original: AudioFile = None  # 无损音质

    def to_dict(self):
        """转换为字典
        """
        return {
            'normal': self.normal.path if self.normal else None,
            'better': self.better.path if self.better else None,
            'high': self.high.path if self.high else None,
            'best': self.best.path if self.best else None,
            'original': self.original.path if self.original else None
        }


class Music:
    """单曲对象
    """
    def __init__(self, path: str = None, import_file: bool = True):
        self.info: MusicInfo = None  # 曲目信息
        self.files: MusicFileList = None  # 音乐文件列表
        self.lyrics: list[Lyric] = []  # 歌词列表
        self.published: bool = False  # 是否已发布
        if path is not None:
            file = AudioFile(path)
            self.files = MusicFileList()
            if import_file:
                # 标记当前文件
                if file.quality == AudioFile.NORMAL:
                    self.files.normal = file
                elif file.quality == AudioFile.BETTER:
                    self.files.better = file
                elif file.quality == AudioFile.HIGH:
                    self.files.high = file
                elif file.quality == AudioFile.BEST:
                    self.files.best = file
                elif file.quality == AudioFile.ORIGINAL:
                    self.files.original = file
            self.info = MusicInfo.load_from_file(file)
