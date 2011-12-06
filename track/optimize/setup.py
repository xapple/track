"""
To compile the python module, type::

    $ python setup.py build

Now you can use it simply like this::

    [1] from track.optimize import bed

    [2] bed.to_sql()
    >>> The C test is working

To compile the standalone C executable, type::

    $ gcc -pthread -fno-strict-aliasing -DNDEBUG -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic -D_GNU_SOURCE -fPIC -fPIC -I/usr/local/include -I/usr/include/python2.6 -c bed.c -o bed.o
    $ gcc -pthread bed.o -L/usr/lib64 -lpython2.6 -lsqlite3 -o bed
"""

from distutils.core import setup, Extension

module = Extension('bed',
                   sources      = ['bed.c'],
                   include_dirs = ['/usr/local/include'],
                   libraries    = ['sqlite3'])

setup(name        = 'Convert BED to SQL',
      version     = '0.1',
      description = 'No description',
      ext_modules = [module])
