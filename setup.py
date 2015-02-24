#!/usr/bin/python
"""A distutils-based script for distributing and installing mcd."""

# Copyright 2014, 2015 Matt Shannon

# This file is part of mcd.
# See `License` for details of license and warranty.

import os
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.sdist import sdist as _sdist

cython_locs = [
    ('mcd', 'metrics_fast'),
]

with open('README.rst') as readme_file:
    long_description = readme_file.read()

# see "A note on setup.py" in README.rst for an explanation of the dev file
dev_mode = os.path.exists('dev')

if dev_mode:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize

    class sdist(_sdist):
        """A cythonizing sdist command.

        This class is a custom sdist command which ensures all cython-generated
        C files are up-to-date before running the conventional sdist command.
        """
        def run(self):
            cythonize([ os.path.join(*loc)+'.pyx' for loc in cython_locs ])
            _sdist.run(self)

    cmdclass = {'build_ext': build_ext, 'sdist': sdist}
    ext_modules = [
        Extension('.'.join(loc), [os.path.join(*loc)+'.pyx'],
                  extra_compile_args=['-Wno-unused-but-set-variable', '-O3'])
        for loc in cython_locs
    ]
else:
    cmdclass = {}
    ext_modules = [
        Extension('.'.join(loc), [os.path.join(*loc)+'.c'],
                  extra_compile_args=['-Wno-unused-but-set-variable', '-O3'])
        for loc in cython_locs
    ]

setup(
    name='mcd',
    version='0.3',
    description='Mel cepstral distortion (MCD) computations in python.',
    url='http://github.com/MattShannon/mcd',
    author='Matt Shannon',
    author_email='matt.shannon@cantab.net',
    license='3-clause BSD (see License file)',
    packages = ['mcd'],
    scripts=[
        os.path.join('bin', 'dtw_synth'),
        os.path.join('bin', 'get_mcd_dtw'),
        os.path.join('bin', 'get_mcd_plain'),
    ],
    long_description = long_description,
    cmdclass = cmdclass,
    ext_modules = ext_modules,
)
