# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import string

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

import hypothesis.strategies as st

text = st.text("абвгдеёжзиклмнопрстуфхцчъыьэюя" + string.ascii_lowercase)
