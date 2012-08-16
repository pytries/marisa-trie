cimport keyset
cimport agent

cdef extern from "../lib/marisa/trie.h" namespace "marisa":

    cdef cppclass Trie:
        Trie()

#        void build(keyset.Keyset &keyset, int config_flags = ?)
        void build(keyset.Keyset &keyset, int config_flags)

        void mmap(char *filename)
        void map(void *ptr, int size)

        void load(char *filename)
        void read(int fd)

        void save(char *filename)
        void write(int fd)

        bint lookup(agent.Agent &agent)
        void reverse_lookup(agent.Agent &agent)
        bint common_prefix_search(agent.Agent &agent)
        bint predictive_search(agent.Agent &agent)

        int num_tries()
        int num_keys()
        int num_nodes()

#        TailMode tail_mode()
#        NodeOrder node_order()

        bint empty()
        int size()
        int total_size()
        int io_size()

        void clear()
        void swap(Trie &rhs)

