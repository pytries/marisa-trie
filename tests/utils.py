# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import sys
import string
from random import choice, randint, randrange

PY3 = sys.version_info[0] == 3

def get_random_words(count):
    russian = 'абвгдеёжзиклмнопрстуфхцчъыьэюя'
    alphabet = russian + string.ascii_lowercase

    def random_word(length):
        return "".join([choice(alphabet) for x in range(randint(1, length))])

    return list(set(random_word(10) for y in range(count)))


def get_random_binary(count):

    if PY3:
        def random_data(length):
            return bytes(randint(0, 255) for x in range(randint(1, length)))
    else:
        def random_data(length):
            return b"".join([chr(randint(0, 255)) for x in range(randint(1, length))])

    return list(set(random_data(10) for y in range(count)))
