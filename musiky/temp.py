# Musiky Python Module https://musiky.sorasky.in/
# Copyright (C) 2021  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Musiky CLI.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.


from sqlalchemy import Column, String, Integer, LargeBinary, JSON, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
from musiky.music import Music
from musiky.uuid import UUID16
import os
import copy
import shutil

Base = declarative_base()


class MusicItem(Base):
    __tablename__ = 'music_item'
    id = Column(Integer, primary_key=True)  # Database field ID
    song_id = Column(String(16))  # Song ID
    title = Column(String)  # Name of song
    artist = Column(String, nullable=True)  # 艺术家
    album = Column(String, nullable=True)  # 专辑
    cover_mime = Column(String, nullable=True)  # 专辑封面MIME
    cover_content = Column(LargeBinary, nullable=True)  # 专辑封面内容
    type = Column(String, nullable=True)  # 歌曲类型
    num = Column(Integer, nullable=True)  # 歌曲专辑内位置
    file = Column(JSON)  # 歌曲文件路径
    lyric = Column(String, nullable=True)  # 歌曲歌词路径
    description = Column(String, nullable=True)  # 备注


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), index=True)
    value = Column(JSON)


class TempDatabase:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        if os.path.exists(self.path):
            self.engine = create_engine('sqlite:///' + self.path, echo=False)
        else:
            self.engine = create_engine('sqlite:///' + self.path, echo=False)
            Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.db_sess = session()

    def new_item(self, item: MusicItem, auto_commit: bool = True):
        self.db_sess.add(item)
        if auto_commit:
            self.db_sess.commit()

    def get_item(self, *args):
        return self.db_sess.query(Config).filter(args).all()

    def remove_item(self, temp_id: Integer):
        self.db_sess.query(Config).filter(Config.pk == temp_id).delete()
        self.db_sess.commit()

    def __getitem__(self, item):
        if self.db_sess.query(exists().where(Config.name == item)).scalar():
            return self.db_sess.query(Config).filter(Config.name == item).first().value[0]
        else:
            return None

    def __setitem__(self, key, value):
        if self.db_sess.query(exists().where(Config.name == key)).scalar():
            self.db_sess.query(Config).filter(Config.name == key).first().value = [value]
        else:
            self.db_sess.add(Config(name=key, value=[value]))
        self.db_sess.commit()


class Temp:
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        if not os.path.exists(path):
            os.mkdir(path)
        self.db = TempDatabase(os.path.join(path, 'temp.db'))
        self.files_path = os.path.join(path, 'files/')
        if not os.path.exists(self.files_path):
            os.mkdir(self.files_path)

    def commit_item(self, music: Music):
        temp_music = copy.deepcopy(music)

        # Generate ID when no ID
        if music.info.id is None:
            temp_music.info.id = UUID16()

        # Copy all music files to temp folder
        for quality, path in music.files.to_dict().items():
            if path:
                new_path = os.path.join(self.files_path, music.info.id + '_' + quality + os.path.splitext(path)[-1])
                if path != new_path:
                    shutil.copyfile(path, new_path)
                    temp_music.files.__dict__[quality].path = new_path

        # Copy cover image to temp folder
        cover_path = music.info.cover[1]
        if cover_path:
            new_path = os.path.join(self.files_path,
                                    music.info.id + '_cover' + os.path.splitext(cover_path)[-1])
            if cover_path != new_path:
                shutil.copyfile(cover_path, new_path)
                temp_music.info.cover[1] = new_path

        # Copy lyric to temp folder
        for i, lyric in enumerate(music.lyrics):
            new_path = os.path.join(self.files_path, music.info.id + '_lyric_' + lyric.lang + '.lrc')
            lyric.export(new_path)
            temp_music.lyrics[i].path = new_path

        # Add to database
        self.db.new_item(MusicItem(
            song_id=temp_music.info.song_id,
            title=temp_music.info.title,
            artist=temp_music.info.artist,
            album=temp_music.info.album,
            cover_mime=temp_music.info.cover[0],
            cover_content=temp_music.info.cover[1],
            type=temp_music.info.type,
            num=temp_music.info.num,
            file=temp_music.files,
            lyric=[lyric.to_dict() for lyric in temp_music.lyrics],
            description=temp_music.info.description
        ))

        return temp_music

    def get_item(self, music_id):
        pass

    def delete_item(self, music_id):
        pass

    def items(self):
        pass

    def temp_info(self):
        pass
