#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 2017-07-13 1:48 AM

'''常用常量保存在这个类里面，以方便以后的统一修改'''
class _const:
    class ConstError(TypeError) : pass

def __setattr__(self, key, value):
        # self.__dict__
        if self.__dict__.has_key(key):
            raise "constant reassignment error!"
        self.__dict__[key] = value

import sys

sys.modules[__name__] = _const()