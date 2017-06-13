
# Copyright 2014, 2015, 2016, 2017 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.

import math
import numpy as np

def sqCepDist(x, y):
    diff = x - y
    return np.inner(diff, diff)

def eucCepDist(x, y):
    diff = x - y
    return math.sqrt(np.inner(diff, diff))

logSpecDbConst = 10.0 / math.log(10.0) * math.sqrt(2.0)
def logSpecDbDist(x, y):
    diff = x - y
    return logSpecDbConst * math.sqrt(np.inner(diff, diff))
