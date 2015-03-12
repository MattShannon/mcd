mcd
===

This package computes mel cepstral distortions in python.
Mel cepstral distortions are used in assessing the quality of synthesized
speech.

Overview
--------

Mel cepstral distortion (MCD) is a measure of how different two sequences of
mel cepstra are.
It is used in assessing the quality of parametric speech synthesis systems,
including statistical parametric speech synthesis systems, the idea being that
the smaller the MCD between synthesized and natural mel cepstral sequences, the
closer the synthetic speech is to reproducing natural speech.
It is by no means a perfect metric for assessing the quality of synthetic
speech, but is often a useful indicator in conjunction with other metrics.

The mcd package provides scripts to compute a variety of forms of MCD score:

- plain MCD, for which it is assumed that the two sequences to be compared are
  already "aligned" in terms of their timing.
- plain MCD excluding certain segments, for example silence segments.
- MCD DTW, which uses dynamic time warping (DTW) to compute the minimum MCD
  obtainable by "aligning" the two sequences.
  This metric does not penalize differences in the timing between natural and
  synthetic speech, which is often desirable.

It also contains general purpose dynamic time warping code.

License
-------

Please see the file ``License`` for details of the license and warranty for
mcd.

Installation
------------

For most purposes the simplest way to install mcd is to use pip.
For example in Debian and Ubuntu::

    sudo apt-get install python-numpy
    sudo pip install mcd

The first command installs numpy from the system repository, since installing
numpy using pip is generally not recommended.
The second command installs the latest released version of
`mcd on PyPI <https://pypi.python.org/pypi/mcd>`_, together with any currently
uninstalled python packages required by mcd.

mcd can also be installed in a virtualenv::

    sudo apt-get install python-numpy
    virtualenv --system-site-packages env
    env/bin/pip install mcd

The latest development version of mcd is available from a github repository
(see below).

To check that mcd is installed correctly you can run the test suite::

    python -m unittest discover mcd

Examples
--------

Examples of example usage (in unix) are given in ``example_usage``.

Development
-----------

The source code is hosted in the
`mcd github repository <https://github.com/MattShannon/mcd>`_.
To obtain the latest source code using git::

    git clone git://github.com/MattShannon/mcd.git

Development is in fact done using `darcs <http://darcs.net/>`_, with the darcs
repository converted to a git repository using
`darcs-to-git <https://github.com/purcell/darcs-to-git>`_.

To install any currently uninstalled python packages required by mcd::

    sudo apt-get install cython python-numpy
    sudo pip install -r requirements.txt

To compile the cython part of mcd in the current directory::

    python setup.py build_ext --inplace

This command must be run after every modification to the source ``.pyx`` files.

To run the full test suite, including tests of command-line tools, on the
working copy::

    python -m unittest discover mcd
    PYTHONPATH=. python bin/test_cli.py

A note on ``setup.py``
----------------------

The included ``setup.py`` file operates in one of two modes depending on
whether or not the file ``dev`` is present in the project root directory.
In development mode (``dev`` present, as for the github repository), the
``build_ext`` command uses cython to compile cython modules from their ``.pyx``
source, and the ``sdist`` command is modified to first use cython to compile
cython modules from their ``.pyx`` source to ``.c`` files.
In distribution mode (``dev`` absent, as for source distributions such as the
code on PyPI), the ``build_ext`` command uses a C compiler to directly compile
cython modules from the corresponding ``.c`` files.
This approach ensures that source distributions can be installed on systems
without cython or with an incompatible version of cython, while ensuring that
distributed ``.c`` files are always up-to-date and that the source ``.pyx``
files are used instead of ``.c`` files during development.

The author would welcome any suggestions for more elegant ways to achieve a
similar effect to the approach described above!

Bugs
----

Please use the
`issue tracker <https://github.com/MattShannon/mcd/issues>`_ to submit bug
reports.

Contact
-------

The author of mcd is `Matt Shannon <mailto:matt.shannon@cantab.net>`_.
