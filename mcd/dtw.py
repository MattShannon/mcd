
# Copyright 2014, 2015, 2016, 2017 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.

import numpy as np
import itertools as it

def getCostMatrix(xs, ys, costFn):
    assert len(xs) > 0 and len(ys) > 0

    costMat = np.array([ [ costFn(x, y) for y in ys ] for x in xs ])
    assert np.shape(costMat) == (len(xs), len(ys))
    return costMat

def getCumCostMatrix(costMat):
    xSize, ySize = np.shape(costMat)

    cumMat = np.zeros((xSize + 1, ySize + 1))
    cumMat[0, 0] = 0.0
    cumMat[0, 1:] = float('inf')
    cumMat[1:, 0] = float('inf')
    for i in range(xSize):
        for j in range(ySize):
            cumMat[i + 1, j + 1] = min(
                cumMat[i, j],
                cumMat[i, j + 1],
                cumMat[i + 1, j]
            )
            cumMat[i + 1, j + 1] += costMat[i, j]

    return cumMat

def getBestPath(cumMat):
    xSize = np.shape(cumMat)[0] - 1
    ySize = np.shape(cumMat)[1] - 1
    assert xSize > 0 and ySize > 0

    i, j = xSize - 1, ySize - 1
    path = [(i, j)]
    while (i, j) != (0, 0):
        _, (i, j) = min(
            (cumMat[i, j], (i - 1, j - 1)),
            (cumMat[i, j + 1], (i - 1, j)),
            (cumMat[i + 1, j], (i, j - 1))
        )
        path.append((i, j))
    path.reverse()

    return path

def dtw(xs, ys, costFn):
    """Computes an alignment of minimum cost using dynamic time warping.

    A path is a sequence of (x-index, y-index) pairs corresponding to a pairing
    of frames in xs to frames in ys.
    The cost of a path is the sum of costFn applied to (x[i], y[j]) for each
    point (i, j) in the path.
    A path is valid if it is:
        - contiguous: neighbouring points on the path are never more than 1
          apart in either x-index or y-index
        - monotone: non-decreasing x-index as we move along the path, and
          similarly for y-index
        - complete: pairs the first frame of xs to the first frame of ys (i.e.
          it starts at (0, 0)) and pairs the last frame of xs to the last frame
          of ys
    Contiguous and monotone amount to saying that the following changes in
    (x-index, y-index) are allowed: (+0, +1), (+1, +0), (+1, +1).
    This function computes the minimum cost a valid path can have.

    Returns the minimum cost and a corresponding path.
    If there is more than one optimal path then one is chosen arbitrarily.
    """
    costMat = getCostMatrix(xs, ys, costFn)
    cumMat = getCumCostMatrix(costMat)
    minCost = cumMat[len(xs), len(ys)]
    path = getBestPath(cumMat)
    return minCost, path

def isValidPath(path):
    if not path:
        return False
    if path[0] != (0, 0):
        return False
    allowedDelta = [(1, 0), (0, 1), (1, 1)]
    for (iPrev, jPrev), (i, j) in zip(path, path[1:]):
        if (i - iPrev, j - jPrev) not in allowedDelta:
            return False
    return True

def swapPath(path):
    return [ (j, i) for i, j in path ]

def projectPathAll(path):
    """Projects a path on to a sequence of sequences of y-indices.

    The resulting sequence has one element for each x-index in the path, and
    each element is the sequence of y-indices which are paired with the x-index
    in the binary relation specified by path.
    """
    yIndicesSeq = []
    for i, subPath in it.groupby(path, lambda iAndJ: iAndJ[0]):
        assert i == len(yIndicesSeq)
        js = [ j for _, j in subPath ]
        yIndicesSeq.append(js)
    return yIndicesSeq

def projectPathMinIndex(path):
    """Projects path on to a sequence of y-indices, one for each x-index.

    Where the path has more than one y-index paired to a given x-index, the
    smallest such y-index is used.
    """
    yIndexSeq = [ min(js) for js in projectPathAll(path) ]
    return yIndexSeq

def projectPathBestCost(path, pathCosts):
    """Projects path on to a sequence of y-indices, one for each x-index.

    Where the path has more than one y-index paired to a given x-index, the
    y-index with smallest cost is used.
    """
    assert len(pathCosts) == len(path)

    # (FIXME : slight abuse of projectPathMinIndex)
    costedYIndexSeq = projectPathMinIndex([
        (i, (cost, j))
        for (i, j), cost in zip(path, pathCosts)
    ])
    yIndexSeq = [ j for _, j in costedYIndexSeq ]
    return yIndexSeq

def findWarpingMinIndex(xs, ys, costFn):
    """Finds a warping of ys with same length as xs using dynamic time warping.

    Where the optimal path has more than one y-index paired to a given x-index,
    the smallest such y-index is used.
    """
    _, path = dtw(xs, ys, costFn)
    yIndexSeq = projectPathMinIndex(path)
    assert len(yIndexSeq) == len(xs)
    return yIndexSeq

def findWarpingBestCost(xs, ys, costFn):
    """Finds a warping of ys with same length as xs using dynamic time warping.

    Where the optimal path has more than one y-index paired to a given x-index,
    the y-index with smallest cost is used.
    """
    _, path = dtw(xs, ys, costFn)
    pathCosts = [ costFn(xs[i], ys[j]) for i, j in path ]
    yIndexSeq = projectPathBestCost(path, pathCosts)
    assert len(yIndexSeq) == len(xs)
    return yIndexSeq

def warpGeneral(ys, yIndexSeq):
    """Warps ys using yIndexSeq."""
    if isinstance(ys, np.ndarray):
        ysWarped = ys[yIndexSeq]
    else:
        ysWarped = [ ys[j] for j in yIndexSeq ]
    assert len(ysWarped) == len(yIndexSeq)
    return ysWarped
