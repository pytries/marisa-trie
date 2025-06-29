import itertools
from pathlib import Path

from Cython.Build import cythonize
from setuptools import setup, Extension


MARISA_ROOT_DIR = Path("marisa-trie")
MARISA_SOURCE_DIR = MARISA_ROOT_DIR / "lib"
MARISA_INCLUDE_DIR = MARISA_ROOT_DIR / "include"
MARISA_FILES = [
    "marisa/*.cc",
    "marisa/grimoire.cc",
    "marisa/grimoire/io/*.cc",
    "marisa/grimoire/trie/*.cc",
    "marisa/grimoire/vector/*.cc",
]

MARISA_FILES[:] = map(str, itertools.chain(
        *(MARISA_SOURCE_DIR.glob(path) for path in MARISA_FILES)
    )
)

extensions = [
    Extension(
        "marisa_trie",
        sources=["src/*.pyx"],
        language="c++",
        include_dirs=[str(MARISA_INCLUDE_DIR)],
    ),
]

setup(
    libraries=[
        (
            "libmarisa-trie",
            {
                "sources": MARISA_FILES,
                "include_dirs": [str(MARISA_SOURCE_DIR), str(MARISA_INCLUDE_DIR)],
            },
        )
    ],
    ext_modules=cythonize(extensions),
)
