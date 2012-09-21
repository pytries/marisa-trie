#! /usr/bin/env python
import glob
import itertools
from distutils.core import setup
from distutils.extension import Extension

MARISA_FILES = [
    'lib/marisa/*.cc',
    'lib/marisa/grimoire.cc',
    'lib/marisa/grimoire/io/*.cc',
    'lib/marisa/grimoire/trie/*.cc',
    'lib/marisa/grimoire/vector/*.cc',
]

MARISA_FILES = list(itertools.chain(*(glob.glob(path) for path in MARISA_FILES)))

setup(
    name="marisa-trie",
    version="0.3.7",
    description="Static memory-efficient & fast Trie structures for Python (based on marisa-trie C++ library)",
    long_description = open('README.rst').read() + open('CHANGES.rst').read(),
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',
    url='https://github.com/kmike/marisa-trie/',

    ext_modules = [
        Extension(
            "marisa_trie",
            sources = glob.glob('src/*.cpp') + MARISA_FILES,
            include_dirs=['lib'],
            language = "c++",
        )
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Text Processing :: Linguistic',
    ],
)
