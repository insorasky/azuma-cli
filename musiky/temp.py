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
import os

Base = declarative_base()


class MusicItem(Base):
    __tablename__ = 'music_item'
    id = Column(Integer, primary_key=True)  # Database field ID
    song_id = Column(String(16))  # Song ID
    title = Column(String)  # Name of song
    artist = Column(String)  # 艺术家
    album = Column(String)  # 专辑
    cover_mime = Column(String)  # 专辑封面MIME
    cover_content = Column(LargeBinary)  # 专辑封面内容
    type = Column(String)  # 歌曲类型
    num = Column(Integer)  # 歌曲专辑内位置
    file = Column(String)  # 歌曲文件路径
    lyric = Column(String)  # 歌曲歌词路径
    description = Column(String)  # 备注


class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), index=True)
    value = Column(JSON)


class TempDatabase:
    def __init__(self, path: str):
        path = os.path.abspath(path)
        self.path = path
        db_path = os.path.join(path, 'temp.db')
        file_path = os.path.join(path, 'files')
        if os.path.exists(db_path):
            self.engine = create_engine('sqlite:///' + db_path, echo=False)
        else:
            self.engine = create_engine('sqlite:///' + db_path, echo=False)
            Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.db_sess = session()
        if os.path.exists(file_path):
            os.mkdir(path)

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
