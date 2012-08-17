cimport keyset
cimport agent

cdef extern from "../lib/marisa/trie.h" namespace "marisa":

    cdef cppclass Trie:
        Trie()

#        void build(keyset.Keyset &keyset, int config_flags = ?)
        void build(keyset.Keyset &keyset, int config_flags) except +

        void mmap(char *filename) except +
        void map(void *ptr, int size) except +

        void load(char *filename) except +
        void read(int fd) except +

        void save(char *filename) except +
        void write(int fd) except +

        bint lookup(agent.Agent &agent) except +
        void reverse_lookup(agent.Agent &agent) except +KeyError
        bint common_prefix_search(agent.Agent &agent) except +
        bint predictive_search(agent.Agent &agent) except +

        int num_tries() except +
        int num_keys() except +
        int num_nodes() except +

#        TailMode tail_mode()
#        NodeOrder node_order()

        bint empty() except +
        int size() except +
        int total_size() except +
        int io_size() except +

        void clear()
        void swap(Trie &rhs)

