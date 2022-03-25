# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma Store Manager Module.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


from sqlalchemy import Column, String, Integer, LargeBinary, JSON, create_engine, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists

from azuma.lyric import Lyric
from azuma.music import Music
from azuma.uuid import UUID16

import datetime
import os
import copy
import shutil

Base = declarative_base()


class MusicItem(Base):
    __tablename__ = 'music_item'
    id = Column(Integer, primary_key=True)  # Database field ID
    song_id = Column(String(16))  # Song ID
    title = Column(String)  # Name of song
    artist = Column(JSON, nullable=True)  # 艺术家
    album = Column(String, nullable=True)  # 专辑
    cover_mime = Column(String, nullable=True)  # 专辑封面MIME
    cover_content = Column(LargeBinary, nullable=True)  # 专辑封面内容
    type = Column(String, nullable=True)  # 歌曲类型
    num = Column(Integer, nullable=True)  # 歌曲专辑内位置
    file = Column(JSON)  # 歌曲文件路径
    lyric = Column(JSON, nullable=True)  # 歌曲歌词
    description = Column(String, nullable=True)  # 备注
    time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # 添加时间


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), index=True)
    value = Column(JSON)
    time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # 添加时间


class EditLog(Base):
    __tablename__ = 'editlog'
    id = Column(Integer, primary_key=True)
    type = Column(Integer)  # 0: add, 1: delete
    uuid = Column(String(16))  # UUID
    time = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)  # 添加时间


class TempDatabase:
    def __init__(self, path: str):
        self.__path = os.path.abspath(path)
        if os.path.exists(self.__path):
            self.__engine = create_engine('sqlite:///' + self.__path, echo=False)
        else:
            self.__engine = create_engine('sqlite:///' + self.__path, echo=False)
            Base.metadata.create_all(self.__engine)
        session = sessionmaker(bind=self.__engine)
        self.__db_sess = session()

    def new_item(self, item: MusicItem, auto_commit: bool = True):
        self.__db_sess.add(item)
        self.__db_sess.add(EditLog(type=0, uuid=str(item.song_id)))
        if auto_commit:
            self.__db_sess.commit()

    def get_item(self, *args):
        return self.__db_sess.query(MusicItem).filter(*args).all()

    def remove_item(self, song_id: UUID16):
        self.__db_sess.query(MusicItem).filter(MusicItem.song_id == str(song_id)).delete()
        self.__db_sess.add(EditLog(type=1, uuid=str(song_id)))
        self.__db_sess.commit()

    def get_edit_log(self, *args):
        return self.__db_sess.query(EditLog).filter(*args).all()

    def __getitem__(self, item):
        if self.__db_sess.query(exists().where(Config.name == item)).scalar():
            return self.__db_sess.query(Config).filter(Config.name == item).first().value
        else:
            return None

    def __setitem__(self, key, value):
        if self.__db_sess.query(exists().where(Config.name == key)).scalar():
            self.__db_sess.query(Config).filter(Config.name == key).first().value = value
        else:
            self.__db_sess.add(Config(name=key, value=value))
        self.__db_sess.commit()

    def __delitem__(self, key):
        self.__db_sess.query(Config).filter(Config.name == key).delete()
        self.__db_sess.commit()


class Temp:
    def __init__(self, path: str):
        self.__path = os.path.abspath(path)
        if not os.path.exists(self.__path):
            os.mkdir(self.__path)
        self.__db = TempDatabase(os.path.join(self.__path, 'temp.db'))
        self.__files_path = os.path.join(self.__path, 'files/')
        if not os.path.exists(self.__files_path):
            os.mkdir(self.__files_path)

        # ID
        if self.__db['id'] is None:
            self.__id = UUID16()
            self.__db['id'] = str(self.__id)
        else:
            self.__id = UUID16(self.__db['id'])

        # Create Time
        if self.__db['create_time'] is None:
            self.__create_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            self.__db['create_time'] = self.__create_time
        else:
            self.__create_time = self.__db['create_time']

    @property
    def id(self):
        return self.__id

    def commit_music(self, music: Music):
        temp_music = copy.deepcopy(music)

        # Generate ID when no ID
        if music.info.id is None:
            temp_music.info.id = UUID16()

        # Copy all music files to temp folder
        for quality, path in music.files.to_dict().items():
            if path:
                new_path = os.path.join(self.__files_path,
                                        str(temp_music.info.id) + '_' + quality + os.path.splitext(path)[-1])
                if path != new_path:
                    shutil.copyfile(path, new_path)
                    temp_music.files.__dict__[quality].__path = new_path

        # Delete if exists
        query = self.__db.get_item(MusicItem.song_id == str(temp_music.info.id))
        if query:
            self.__db.remove_item(temp_music.info.id)

        # Add to database
        self.__db.new_item(MusicItem(
            song_id=str(temp_music.info.id),
            title=temp_music.info.title,
            artist=temp_music.info.artist,
            album=temp_music.info.album,
            cover_mime=temp_music.info.cover[0],
            cover_content=temp_music.info.cover[1],
            type=temp_music.info.type,
            num=temp_music.info.num,
            file=temp_music.files.to_dict(),
            lyric=[lyric.to_dict() for lyric in temp_music.lyrics],
            description=temp_music.info.description
        ))

        return temp_music

    def get_music(self, song_id) -> Music:
        tmp = Music()
        query = self.__db.get_item(MusicItem.song_id == str(song_id))
        if query:
            tmp.info.id = UUID16(query[0].song_id)
            tmp.info.title = query[0].title
            tmp.info.artist = query[0].artist
            tmp.info.album = query[0].album
            tmp.info.cover = (query[0].cover_mime, query[0].cover_content)
            tmp.info.type = query[0].type
            tmp.info.num = query[0].num
            tmp.info.description = query[0].description
            tmp.files.from_dict(query[0].file)
            tmp.lyrics = [Lyric.from_dict(lyric) for lyric in query[0].lyric]
            return tmp
        else:
            raise KeyError('No music with id {}'.format(song_id))

    def delete_music(self, song_id):
        query = self.__db.get_item(MusicItem.song_id == str(song_id))
        if query:
            self.__db.remove_item(song_id)
        else:
            raise KeyError('No music with id {}'.format(song_id))

    def all_items(self) -> list[tuple[UUID16, str]]:
        query = self.__db.get_item()
        return [(UUID16(item.song_id), item.title) for item in query]

    def config(self, key, value=None):
        if value is None:
            return self.__db[key]
        else:
            self.__db[key] = value

    def unset(self, key):
        del self.__db[key]

    @property
    def name(self):
        return self.__db['name']

    @name.setter
    def name(self, value):
        self.__db['name'] = value

    @property
    def maintainer(self):
        return self.__db['maintainer']

    @maintainer.setter
    def maintainer(self, value):
        self.__db['maintainer'] = value

    @property
    def description(self):
        return self.__db['description']

    @description.setter
    def description(self, value):
        self.__db['description'] = value

    def get_edit_log(self, timestamp: float = 0) -> list[tuple[int, UUID16]]:
        query = self.__db.get_edit_log(EditLog.time > datetime.datetime.fromtimestamp(timestamp))
        return [(item.type, UUID16(item.uuid)) for item in query]
