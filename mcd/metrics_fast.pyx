
# Copyright 2014, 2015, 2016, 2017 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.


import math
import numpy as np

from libc.math cimport log, sqrt
cimport numpy as cnp
cimport cython

cnp.import_array()
cnp.import_ufunc()

@cython.boundscheck(False)
def sqCepDist(cnp.ndarray[cnp.float64_t, ndim=1] x,
              cnp.ndarray[cnp.float64_t, ndim=1] y):
    cdef unsigned int k, size
    cdef double diff, sumSqDiff

    size = x.shape[0]
    assert y.shape[0] == size

    sumSqDiff = 0.0
    for k in range(size):
        diff = x[k] - y[k]
        sumSqDiff += diff * diff

    return sumSqDiff

@cython.boundscheck(False)
def eucCepDist(cnp.ndarray[cnp.float64_t, ndim=1] x,
               cnp.ndarray[cnp.float64_t, ndim=1] y):
    cdef unsigned int k, size
    cdef double diff, sumSqDiff, dist

    size = x.shape[0]
    assert y.shape[0] == size

    sumSqDiff = 0.0
    for k in range(size):
        diff = x[k] - y[k]
        sumSqDiff += diff * diff

    dist = sqrt(sumSqDiff)
    return dist

cdef double logSpecDbConst = 10.0 / log(10.0) * sqrt(2.0)

@cython.boundscheck(False)
def logSpecDbDist(cnp.ndarray[cnp.float64_t, ndim=1] x,
                  cnp.ndarray[cnp.float64_t, ndim=1] y):
    cdef unsigned int k, size
    cdef double diff, sumSqDiff, dist

    size = x.shape[0]
    assert y.shape[0] == size

    sumSqDiff = 0.0
    for k in range(size):
        diff = x[k] - y[k]
        sumSqDiff += diff * diff

    dist = sqrt(sumSqDiff) * logSpecDbConst
    return dist
