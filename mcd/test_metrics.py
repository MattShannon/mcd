
# Copyright 2014, 2015, 2016, 2017 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.

import unittest
import math
import numpy as np
import random
from numpy.random import randn, randint

import mcd.metrics as mt
import mcd.metrics_fast as mtf
from mcd.util import assert_allclose

def randBool():
    return randint(0, 2) == 0

class TestMetrics(unittest.TestCase):
    def test_sqCepDist(self, numPoints=100):
        # (FIXME : not a proper unit test: doesn't really check correctness)
        for _ in range(numPoints):
            size = random.choice([0, 1, randint(0, 10), randint(0, 100)])
            x = randn(size)
            y = randn(size)

            # check fast and slow versions agree
            assert_allclose(mtf.sqCepDist(x, y), mt.sqCepDist(x, y))

            # check both versions raise an error where appropriate
            y = randn(size + 1)
            if size > 1:
                self.assertRaises(ValueError, mt.sqCepDist, x, y)
            self.assertRaises(AssertionError, mtf.sqCepDist, x, y)

    def test_eucCepDist(self, numPoints=100):
        # (FIXME : not a proper unit test: doesn't really check correctness)
        for _ in range(numPoints):
            size = random.choice([0, 1, randint(0, 10), randint(0, 100)])
            x = randn(size)
            y = randn(size)

            # check fast and slow versions agree
            assert_allclose(mtf.eucCepDist(x, y), mt.eucCepDist(x, y))

            # check both versions raise an error where appropriate
            y = randn(size + 1)
            if size > 1:
                self.assertRaises(ValueError, mt.eucCepDist, x, y)
            self.assertRaises(AssertionError, mtf.eucCepDist, x, y)

    def test_logSpecDbDist(self, numPoints=100):
        # (FIXME : not a proper unit test: doesn't really check correctness)
        for _ in range(numPoints):
            size = random.choice([0, 1, randint(0, 10), randint(0, 100)])
            x = randn(size)
            y = randn(size)

            # check fast and slow versions agree
            assert_allclose(mtf.logSpecDbDist(x, y), mt.logSpecDbDist(x, y))

            # check both versions raise an error where appropriate
            y = randn(size + 1)
            if size > 1:
                self.assertRaises(ValueError, mt.logSpecDbDist, x, y)
            self.assertRaises(AssertionError, mtf.logSpecDbDist, x, y)

if __name__ == '__main__':
    unittest.main()
