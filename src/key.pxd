cdef extern from "../lib/marisa/key.h" namespace "marisa":

    cdef cppclass Key:
        Key() nogil
        Key(Key &query) nogil

        #Key &operator=(Key &query)

        char operator[](int i) nogil

        void set_str(char *str) nogil
        void set_str(char *ptr, int length) nogil
        void set_id(int id) nogil
        void set_weight(float weight) nogil

        char *ptr() nogil
        int length() nogil
        int id() nogil
        float weight() nogil

        void clear() nogil
        void swap(Key &rhs) nogil