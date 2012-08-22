cimport query, key

cdef extern from "../lib/marisa/keyset.h" namespace "marisa":
    cdef cppclass Keyset:

#        cdef enum constants:
#            BASE_BLOCK_SIZE  = 4096
#            EXTRA_BLOCK_SIZE = 1024
#            KEY_BLOCK_SIZE   = 256

        Keyset() nogil

        void push_back(key.Key &key) nogil
        void push_back(key.Key &key, char end_marker) nogil

        void push_back(char *str) nogil
        void push_back(char *ptr, int length) nogil
        void push_back(char *ptr, int length, float weight) nogil

        key.Key &operator[](int i) nogil

        int num_keys() nogil
        bint empty() nogil

        int size() nogil
        int total_length() nogil

        void reset() nogil
        void clear() nogil
        void swap(Keyset &rhs) nogil
