cimport query, key

cdef extern from "../lib/marisa/agent.h" namespace "marisa":
    cdef cppclass Agent:
        Agent() except +

        query.Query &query() nogil
        key.Key &key() nogil

        void set_query(char *str) nogil
        void set_query(char *ptr, int length) nogil
        void set_query(int key_id) nogil

        void set_key(char *str) nogil
        void set_key(char *ptr, int length) nogil
        void set_key(int id) nogil

        void clear() nogil

        void init_state() nogil

        void swap(Agent &rhs) nogil

