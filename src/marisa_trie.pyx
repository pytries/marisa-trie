cimport keyset
cimport key
cimport query
cimport agent
cimport trie


cdef class Trie:

    cdef trie.Trie* _trie

    def __cinit__(self):
        self._trie = new trie.Trie()

    def __dealloc__(self):
        if self._trie:
            del self._trie

    def __getitem__(self, unicode key):
        cdef bytes _key = key.encode('utf8')
        try:
            return self._getitem(_key)
        except KeyError:
            raise KeyError(key)

    def __contains__(self, unicode key):
        cdef bytes _key = key.encode('utf8')
        return self._contains(_key)


    cdef int _getitem(self, char* key) except -1:
        cdef bint res
        cdef agent.Agent ag
        ag.set_query(key)
        res = self._trie.lookup(ag)
        if not res:
            raise KeyError(key)
        return ag.key().id()

    cdef bint _contains(self, char* key):
        cdef agent.Agent ag
        ag.set_query(key)
        return self._trie.lookup(ag)

    def read(self, f):
        self._trie.read(f.fileno())

    def write(self, f):
        self._trie.read(f.fileno())

#        void build(keyset.Keyset &keyset, int config_flags = ?)
#        void mmap(char *filename)
#        void map(void *ptr, int size)
#
#        void load(char *filename)
#        void read(int fd)
#
#        void save(char *filename)
#        void write(int fd)


cdef class Keyset:
    pass