# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import string
import hypothesis.strategies as st

text = st.text("абвгдеёжзиклмнопрстуфхцчъыьэюя" + string.ascii_lowercase)
