from sage.structure.parent_gens cimport ParentWithGens

cpdef bint _is_Field(x) except -2

cdef class Ring(ParentWithGens):
    cdef public object _zero_element
    cdef public object _one_element
    cdef public object _zero_ideal
    cdef public object _unit_ideal
    cdef public object _ideal_monoid


cdef class CommutativeRing(Ring):
    cdef public object __fraction_field

cdef class IntegralDomain(CommutativeRing):
    pass

cdef class DedekindDomain(CommutativeRing):
    pass

cdef class PrincipalIdealDomain(CommutativeRing):
    pass

cdef class Field(CommutativeRing):
    pass

cdef class Algebra(Ring):
    pass

cdef class CommutativeAlgebra(CommutativeRing):
    pass
