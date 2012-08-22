from std_iostream cimport istream, ostream
from trie cimport Trie

cdef extern from "../lib/marisa/iostream.h" namespace "marisa":

    istream &read(istream &stream, Trie *trie) nogil
    ostream &write(ostream &stream, Trie &trie) nogil
