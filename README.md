track 1.0.0
===========

Copyright 2011 EPFL BBCF <webmaster@epfl.ch>

track is a python module for reading and writing genomic
data.

It was developed by the Bioinformatics and Biostatistics Core
Facility (BBCF) at the EPFL.

track is released under the GNU General Public License 3.0. A copy
of this license is in the LICENSE.txt file.

Installation
============

track requires:
* Python 2.6 or higher

To install you should download the latest source code from GitHub,
either by going to:

    http://github.com/bbcf/track

and clicking on "Downloads", or by cloning the git repository with

    $ git clone https://github.com/bbcf/track.git

Once you have the source code, run

    $ python setup.py build
    $ sudo python setup.py install

to install it. If you need to install it in a particular directory,
use

    $ sudo python setup.py install --prefix=/prefix/path

Then the modules will go in /prefix/path/lib/pythonX.Y/site-packages,
where X.Y is the version of Python you run it with.

To run the test suite, in the distribution directory, run

    $ nosetests

Full documentation
==================

The full documentation can be found [on our website](http://bbcf.epfl.ch/track).
