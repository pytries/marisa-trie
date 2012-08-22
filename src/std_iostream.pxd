from libcpp.string cimport string

cdef extern from "<istream>" namespace "std":
    cdef cppclass istream:
        istream() nogil except +
        istream& read (char* s, int n) nogil except +

    cdef cppclass ostream:
        ostream() nogil except +
        ostream& write (char* s, int n) nogil except +

cdef extern from "<sstream>" namespace "std":

    cdef cppclass stringstream:
        stringstream() nogil
        stringstream(string s) nogil
        string str () nogil

