# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

if sys.version_info[:1] > (2, 6):
    import string
    import hypothesis.strategies as st

    text = st.text("абвгдеёжзиклмнопрстуфхцчъыьэюя" + string.ascii_lowercase)
