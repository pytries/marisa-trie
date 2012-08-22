cimport keyset
cimport agent

cdef extern from "../lib/marisa/trie.h" namespace "marisa":

    cdef cppclass Trie:
        Trie()

        void build(keyset.Keyset &keyset, int config_flags) nogil except +
        void build(keyset.Keyset &keyset) nogil except +

        void mmap(char *filename) nogil except +
        void map(void *ptr, int size) except +

        void load(char *filename) nogil except +
        void read(int fd) nogil except +

        void save(char *filename) nogil except +
        void write(int fd) nogil except +

        bint lookup(agent.Agent &agent) except +
        void reverse_lookup(agent.Agent &agent) except +KeyError
        bint common_prefix_search(agent.Agent &agent) except +
        bint predictive_search(agent.Agent &agent) except +

        int num_tries() nogil except +
        int num_keys() nogil except +
        int num_nodes() nogil except +

#        TailMode tail_mode()
#        NodeOrder node_order()

        bint empty() nogil except +
        int size() nogil except +
        int total_size() nogil except +
        int io_size() nogil except +

        void clear() nogil except +
        void swap(Trie &rhs) nogil except +

