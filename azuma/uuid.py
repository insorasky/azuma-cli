# Azuma Python Module https://azuma.sorasky.in/
# Copyright (C) 2022  Sora
# ALL RIGHTS RESERVED.
#
# The module is a part of Azuma Store Manager Module.
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import uuid
from .exception import UUID16InvalidException

byte = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'  # 共62字符


def is_uuid16(u: str):
    if len(u) != 16:
        return False
    for c in u:
        if c not in byte:
            return False
    return True


class UUID16:
    """
        Azuma使用的16位UUID的生成规则为：

        1、使用通用的UUID生成器生成整数形式的UUID；

        2、将该UUID对62取余16次；

        3、将生成的16个整数变换为字符，整数剩余部分丢弃。
    """

    def __init__(self, u=None):
        if u is None:
            uuid_i = uuid.uuid4().int
            self._u = ''
            for i in range(0, 16):
                self._u += byte[uuid_i % len(byte)]
                uuid_i = int(uuid_i / len(byte))
        else:
            if is_uuid16(u):
                self._u = u
            else:
                raise UUID16InvalidException(u)

    def __repr__(self):
        return f'UUID16({self._u})'

    def __str__(self):
        return self._u
