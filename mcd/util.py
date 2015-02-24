
# Copyright 2014, 2015 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.


import numpy as np

def assert_allclose(actual, desired, rtol=1e-7, atol=1e-14,
                    msg='items not almost equal'):
    if np.shape(actual) != np.shape(desired):
        raise AssertionError('%s (wrong shape)\n ACTUAL:  %r\n DESIRED: %r' %
                             (msg, actual, desired))
    if not np.allclose(actual, desired, rtol, atol):
        absErr = np.abs(actual - desired)
        relErr = np.abs((actual - desired) / desired)
        raise AssertionError('%s\n ACTUAL:  %r\n DESIRED: %r\n'
                             ' ABS ERR: %r (max %s)\n REL ERR: %r (max %s)' %
                             (msg, actual, desired,
                              absErr, np.max(absErr), relErr, np.max(relErr)))

def readParamFileAlt(paramFile, paramOrder):
    return np.reshape(
        np.fromfile(paramFile, dtype=np.float32),
        (-1, paramOrder)
    ).astype(np.float64)

def writeParamFile(outSeq, paramFile, paramOrder=None):
    outSeq.astype(np.float32).tofile(paramFile)

def readLabFile(labFile, framePeriod):
    divisor = framePeriod * 1.0e7
    for line in open(labFile):
        splitLine = line.strip().split(None, 2)
        if len(splitLine) == 1:
            label, = splitLine
            yield None, None, label
        else:
            startTicks, endTicks, label = splitLine
            startTime = int(int(startTicks) / divisor + 0.5)
            endTime = int(int(endTicks) / divisor + 0.5)
            yield startTime, endTime, label

def expandAlignment(alignment):
    checkedOverallStartTime = False
    endTimePrev = None
    for startTime, endTime, label in alignment:
        if not checkedOverallStartTime:
            assert startTime == 0
            checkedOverallStartTime = True
        assert endTimePrev is None or startTime == endTimePrev
        assert endTime >= startTime
        for i in range(endTime - startTime):
            yield label
        endTimePrev = endTime
