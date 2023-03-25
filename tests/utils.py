import string
from collections.abc import Mapping

import hypothesis.strategies as st

text = st.text(f"абвгдеёжзиклмнопрстуфхцчъыьэюя{string.ascii_lowercase}")

__all__ = ("Mapping", text)
