"""Static memory-efficient and fast Trie-like structures for Python."""

import glob
import itertools
import os.path

from setuptools import setup, Extension

# Note: keep requirements here to ease distributions packaging
tests_require = [
    "pytest",
    "hypothesis",
]
install_requires = [
    "setuptools",
]

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

DESCRIPTION = __doc__
with open("README.rst", encoding="utf-8") as f1, open(
    "CHANGES.rst", encoding="utf-8"
) as f2:
    LONG_DESCRIPTION = f1.read() + f2.read()
LICENSE = "MIT"

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Cython",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Text Processing :: Linguistic",
]

setup(
    name="marisa-trie",
    version="0.7.5",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author="Mikhail Korobov",
    author_email="kmike84@gmail.com",
    license=LICENSE,
    url="https://github.com/kmike/marisa-trie",
    classifiers=CLASSIFIERS,
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
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=install_requires,
    extras_require={
        "test": tests_require,
    },
)
