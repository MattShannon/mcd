"""Unit tests for command-line tools.

Many of these tests take the form of characterization tests which verify that
the behaviour does not change but not that it is correct.
"""

# Copyright 2014, 2015, 2016, 2017 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.

import unittest
import os
from os.path import join
import sys
import logging
import subprocess
from subprocess import PIPE
import shutil
import tempfile
from filecmp import cmpfiles

# (FIXME : bit of a hacky way to find base dir)
import mcd as mcd_temp
baseDir = os.path.dirname(os.path.dirname(mcd_temp.__file__))
print '(using baseDir %s)' % baseDir

class TempDir(object):
    def __init__(self, prefix='mcd.', removeOnException=False):
        self.prefix = prefix
        self.removeOnException = removeOnException

    def __enter__(self):
        self.location = tempfile.mkdtemp(prefix=self.prefix)
        return self

    def remove(self):
        shutil.rmtree(self.location)

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None or self.removeOnException:
            self.remove()
        if os.path.isdir(self.location):
            logging.warning('temporary directory %s not deleted. You probably'
                            ' want to do this manually after looking at its'
                            ' contents.' % self.location)

def readUttIds(uttIdsFile):
    return [ line.strip() for line in open(uttIdsFile) ]

# FIXME : replace exact equality with allclose in lots of the tests below?

class TestCliTools(unittest.TestCase):
    def test_dtw_synth(self):
        """Simple characterization test for dtw_synth."""
        uttIds = readUttIds(join(baseDir, 'test_data', 'corpus.lst'))
        with TempDir() as tempDir:
            synthOutDir = tempDir.location
            p = subprocess.Popen([
                sys.executable,
                join(baseDir, 'bin', 'dtw_synth'),
                '--exts', 'mgc,lf0,bap',
                '--param_orders', '40,1,5',
                join(baseDir, 'test_data', 'ref-examples'),
                join(baseDir, 'test_data', 'synth-examples'),
                synthOutDir,
            ] + uttIds, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            stdoutGood = (
                'processing cmu_us_arctic_slt_a0003\n'
                'MCD = 6.175330 (641 frames)\n'
                'warping 683 frames -> 641 frames (29 repeated, 71 dropped)\n'
                '\n'
                'processing cmu_us_arctic_slt_a0044\n'
                'MCD = 5.577534 (613 frames)\n'
                'warping 653 frames -> 613 frames (35 repeated, 75 dropped)\n'
                '\n'
                'overall MCD = 5.883106 (1254 frames)\n'
            )
            self.assertEqual(stderr, '')
            self.assertEqual(stdout, stdoutGood)
            synthOutDirGood = join(baseDir, 'test_data', 'out-dtw_synth')
            filenames = [ '%s.mgc' % uttId for uttId in uttIds ]
            match, mismatch, errors = cmpfiles(synthOutDir, synthOutDirGood,
                                               filenames, shallow = False)
            self.assertEqual(match, filenames)
            self.assertFalse(mismatch)
            self.assertFalse(errors)

    def test_get_mcd_dtw(self):
        """Simple characterization test for get_mcd_dtw."""
        uttIds = readUttIds(join(baseDir, 'test_data', 'corpus.lst'))
        p = subprocess.Popen([
            sys.executable,
            join(baseDir, 'bin', 'get_mcd_dtw'),
            '--ext', 'mgc',
            '--param_order', '40',
            join(baseDir, 'test_data', 'ref-examples'),
            join(baseDir, 'test_data', 'synth-examples'),
        ] + uttIds, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        stdoutGood = (
            'processing cmu_us_arctic_slt_a0003\n'
            'processing cmu_us_arctic_slt_a0044\n'
            'overall MCD = 5.883106 (1254 frames)\n'
        )
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, stdoutGood)

    def test_get_mcd_plain(self):
        """Simple characterization test for get_mcd_plain."""
        uttIds = readUttIds(join(baseDir, 'test_data', 'corpus.lst'))
        p = subprocess.Popen([
            sys.executable,
            join(baseDir, 'bin', 'get_mcd_plain'),
            '--ext', 'mgc',
            '--param_order', '40',
            join(baseDir, 'test_data', 'ref-examples'),
            join(baseDir, 'test_data', 'aligned-synth-examples'),
        ] + uttIds, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        stdoutGood = (
            'processing cmu_us_arctic_slt_a0003\n'
            'processing cmu_us_arctic_slt_a0044\n'
            'overall MCD = 5.308880 (1254 frames)\n'
        )
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, stdoutGood)

    def test_get_mcd_plain_exc_pau(self):
        """Simple characterization test for get_mcd_plain excluding pau."""
        uttIds = readUttIds(join(baseDir, 'test_data', 'corpus.lst'))
        alignmentDir = join(
            baseDir, 'test_data', 'aligned-synth-examples', 'alignment'
        )
        p = subprocess.Popen([
            sys.executable,
            join(baseDir, 'bin', 'get_mcd_plain'),
            '--ext', 'mgc',
            '--param_order', '40',
            '--remove_segments', '.-pau\+',
            '--alignment_dir', alignmentDir,
            '--frame_period', '0.005',
            join(baseDir, 'test_data', 'ref-examples'),
            join(baseDir, 'test_data', 'aligned-synth-examples'),
        ] + uttIds, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        stdoutGood = (
            'NOTE: removing segments matching regex \'.-pau\+\' using'
            ' alignments in %s\n'
            'processing cmu_us_arctic_slt_a0003\n'
            'processing cmu_us_arctic_slt_a0044\n'
            'overall MCD = 5.389857 (1157 frames)\n'
        ) % alignmentDir
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, stdoutGood)

if __name__ == '__main__':
    unittest.main()
