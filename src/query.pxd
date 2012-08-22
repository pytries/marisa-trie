cdef extern from "../lib/marisa/query.h" namespace "marisa":

    cdef cppclass Query:
        Query() nogil
        Query(Query &query) nogil

        #Query &operator=(Query &query)

        char operator[](int i) nogil

        void set_str(char *str) nogil
        void set_str(char *ptr, int length) nogil
        void set_id(int id) nogil

        char *ptr() nogil
        int length() nogil
        int id() nogil

        void clear() nogil
        void swap(Query &rhs) nogil