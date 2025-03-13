"""Static memory-efficient and fast Trie-like structures for Python."""

import glob
import itertools
import os.path

from setuptools import setup, Extension


# Note: keep requirements here to ease distributions packaging
tests_require = [
    "hypothesis",
    "pytest",
    "readme_renderer",
]
setup_requires = [
    "setuptools",
]
install_requires = []

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
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Text Processing :: Linguistic",
]

setup(
    name="marisa-trie",
    version="1.2.1",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    author="Mikhail Korobov",
    author_email="kmike84@gmail.com",
    license=LICENSE,
    url="https://github.com/pytries/marisa-trie",
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
    python_requires=">=3.8",
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require={
        "test": tests_require,
    },
)
