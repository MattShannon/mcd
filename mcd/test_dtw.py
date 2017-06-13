
# Copyright 2014, 2015, 2016, 2017 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.

import unittest
import math
import numpy as np
import random
from numpy.random import randn, randint

from mcd import dtw
from mcd.util import assert_allclose

def randBool():
    return randint(0, 2) == 0

def randSeq(dim, minLength=0, ensureShort=False):
    length = (randint(minLength, 4) if ensureShort or randBool()
              else randint(minLength, 100))
    xs = randn(length, dim)
    return xs

def getPathCost(path, xs, ys, costFn):
    return sum([ costFn(xs[i], ys[j]) for i, j in path ])

def sqCost(x, y):
    return np.inner(x - y, x - y)
def eucCost(x, y):
    return math.sqrt(np.inner(x - y, x - y))

def getDagPathIterator(childrenDict, startNode):
    """Returns an iterator over full paths through a DAG starting at a node.

    Here DAG stands for directed acyclic graph.
    A full path is a path for which the last node has no children.
    """
    def isLastChild(node, childIndex):
        return childIndex == len(childrenDict[node]) - 1

    nodeSeq = [startNode]
    childIndexSeq = []
    while True:
        if childrenDict[nodeSeq[-1]]:
            nodeSeq.append(childrenDict[nodeSeq[-1]][0])
            childIndexSeq.append(0)
        else:
            yield list(nodeSeq), list(childIndexSeq)

            while (childIndexSeq and
                   isLastChild(nodeSeq[-2], childIndexSeq[-1])):
                nodeSeq.pop()
                childIndexSeq.pop()
            if not childIndexSeq:
                return
            else:
                childIndex = childIndexSeq[-1] + 1
                nodeSeq[-1] = childrenDict[nodeSeq[-2]][childIndex]
                childIndexSeq[-1] = childIndex

def getRandomDagPath(childrenDict, startNode):
    """Returns a random full path through a directed acyclic graph.

    A full path is a path for which the last node has no children.
    N.B. the distribution used is *not* the uniform distribution over full
    paths.
    """
    nodeSeq = [startNode]
    while childrenDict[nodeSeq[-1]]:
        nodeSeq.append(random.choice(childrenDict[nodeSeq[-1]]))

    return nodeSeq

def getDtwDag(xSize, ySize):
    """Returns a DTW-style directed acyclic graph."""
    def isValid(node):
        i, j = node
        return 0 <= i < xSize and 0 <= j < ySize

    def getChildren(node):
        i, j = node
        possChildren = [(i + 1, j), (i + 1, j + 1), (i, j + 1)]
        children = filter(isValid, possChildren)
        return children

    childrenDict = dict()
    for i in range(xSize):
        for j in range(ySize):
            node = (i, j)
            childrenDict[node] = getChildren(node)

    startNode = (0, 0)
    assert isValid(startNode)

    return childrenDict, startNode

class TestDtw(unittest.TestCase):
    def test_empty_seq_raises_exception(self):
        self.assertRaises(AssertionError, dtw.dtw, [], [], eucCost)
        self.assertRaises(AssertionError, dtw.dtw, [], [0.0], eucCost)
        self.assertRaises(AssertionError, dtw.dtw, [0.0], [], eucCost)

    def test_length_one_seq(self, numPairs=100):
        for pair in range(numPairs):
            x = randn()
            y = randn()
            minCost, path = dtw.dtw([x], [y], eucCost)
            assert_allclose(minCost, abs(x - y))
            assert path == [(0, 0)]

    def test_one_length_one_seq(self, numPairs=100):
        for pair in range(numPairs):
            xs = randn(randint(1, 10))
            y = randn()
            minCost, path = dtw.dtw(xs, [y], eucCost)
            assert_allclose(minCost, sum([ abs(x - y) for x in xs]))
            assert path == [ (i, 0) for i in range(len(xs)) ]

    def test_brute_force_small(self, numPairs=100):
        for pair in range(numPairs):
            dim = randint(0, 3) if randBool() else randint(0, 10)
            xs = randSeq(dim=dim, minLength=1, ensureShort=True)
            ys = randSeq(dim=dim, minLength=1, ensureShort=True)

            childrenDict, startNode = getDtwDag(len(xs), len(ys))
            minCostGood = min([
                getPathCost(path, xs, ys, eucCost)
                for path, _ in getDagPathIterator(childrenDict, startNode)
            ])

            minCost, _ = dtw.dtw(xs, ys, eucCost)
            assert_allclose(minCost, minCostGood)

    def test_universal_properties(self, numPairs=100, numPathsPerPair=20):
        for pair in range(numPairs):
            dim = randint(0, 3) if randBool() else randint(0, 10)
            xs = randSeq(dim=dim, minLength=1)
            ys = randSeq(dim=dim, minLength=1)
            minCost, path = dtw.dtw(xs, ys, eucCost)

            # test cost along path agrees with minimum cost
            assert_allclose(minCost, getPathCost(path, xs, ys, eucCost))

            # test transpose
            minCost2, path2 = dtw.dtw(ys, xs, eucCost)
            assert_allclose(minCost2, minCost)
            # N.B. this is not a universal property but will almost always be
            #   true for the random sequences of floats that we generate.
            assert path2 == dtw.swapPath(path)

            # test path is a valid path
            assert dtw.isValidPath(path)
            assert path[-1] == (len(xs) - 1, len(ys) - 1)

            # test optimal subpaths property
            cutIndex = randint(len(path))
            iCut, jCut = path[cutIndex]
            pathA = path[:(cutIndex + 1)]
            pathB = path[cutIndex:]
            costA = getPathCost(pathA, xs, ys, eucCost)
            costB = getPathCost(pathB, xs, ys, eucCost)
            minCostA, _ = dtw.dtw(xs[:(iCut + 1)], ys[:(jCut + 1)], eucCost)
            minCostB, _ = dtw.dtw(xs[iCut:], ys[jCut:], eucCost)
            assert_allclose(costA, minCostA)
            assert_allclose(costB, minCostB)

            # test minCost <= cost for several randomly generated paths
            childrenDict, startNode = getDtwDag(len(xs), len(ys))
            for _ in range(numPathsPerPair):
                path = getRandomDagPath(childrenDict, startNode)
                cost = getPathCost(path, xs, ys, eucCost)
                assert minCost <= cost or np.allclose(minCost, cost)

            # minCost to itself should be zero
            assert dtw.dtw(xs, xs, eucCost)[0] == 0.0

    def test_projectPathAll(self, numPaths=100):
        for _ in range(numPaths):
            path = []
            for i in range(randint(1, 6)):
                for _ in range(randint(1, 4)):
                    path.append((i, randint(20)))

            yIndicesSeq = dtw.projectPathAll(path)

            pathAgain = [
                (i, j)
                for i, yIndices in enumerate(yIndicesSeq)
                for j in yIndices
            ]
            assert pathAgain == path

    def test_projectPathBestCost(self, numPaths=100):
        for _ in range(numPaths):
            childrenDict, startNode = getDtwDag(randint(1, 10), randint(1, 10))
            path = getRandomDagPath(childrenDict, startNode)
            pathCosts = randn(len(path))

            yIndexSeq = dtw.projectPathBestCost(path, pathCosts)

            # (FIXME : code below is not very transparent)
            yIndicesSeq = dtw.projectPathAll(path)
            assert len(yIndexSeq) == len(yIndicesSeq)
            costsSeq = dtw.projectPathAll([
                (i, cost)
                for (i, j), cost in zip(path, pathCosts)
            ])
            assert len(costsSeq) == len(yIndicesSeq)
            for j, js, costs in zip(yIndexSeq, yIndicesSeq, costsSeq):
                minCost = min(costs)
                assert j in [
                    j2
                    for j2, cost in zip(js, costs)
                    if cost == minCost
                ]

if __name__ == '__main__':
    unittest.main()
