import glob
import itertools
import os.path

from setuptools import setup, Extension


MARISA_ROOT_DIR = "marisa-trie"
MARISA_SOURCE_DIR = os.path.join(MARISA_ROOT_DIR, "lib")
MARISA_INCLUDE_DIR = os.path.join(MARISA_ROOT_DIR, "include")
MARISA_FILES = [
    "marisa/*.cc",
    "marisa/grimoire.cc",
    "marisa/grimoire/io/*.cc",
    "marisa/grimoire/trie/*.cc",
    "marisa/grimoire/vector/*.cc",
]

MARISA_FILES[:] = itertools.chain(
    *(glob.glob(os.path.join(MARISA_SOURCE_DIR, path)) for path in MARISA_FILES)
)


setup(
    libraries=[
        (
            "libmarisa-trie",
            {
                "sources": MARISA_FILES,
                "include_dirs": [MARISA_SOURCE_DIR, MARISA_INCLUDE_DIR],
            },
        )
    ],
    ext_modules=[
        Extension(
            "marisa_trie",
            [
                "src/agent.cpp",
                "src/base.cpp",
                "src/iostream.cpp",
                "src/key.cpp",
                "src/keyset.cpp",
                "src/marisa_trie.cpp",
                "src/query.cpp",
                "src/std_iostream.cpp",
                "src/trie.cpp",
            ],
            include_dirs=[MARISA_INCLUDE_DIR],
        )
    ],
)
