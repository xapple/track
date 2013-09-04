try:
    from setuptools import setup, Extension
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Extension

from track import __version__


setup(
        name             =   'track',
        version          =   __version__,
        description      =   'Python package for reading and writing genomic data',
        long_description =   open('README.md').read(),
        license          =   'GNU General Public License 3.0',
        url              =   'http://xapple.github.com/track/',
        author           =   'Lucas Sinclair',
        author_email     =   'lucas.sinclair@me.com',
        classifiers      =   ['Topic :: Scientific/Engineering :: Bio-Informatics'],
        packages         =   ['track',
                              'track.parse',
                              'track.serialize',
                              'track.test',
                              'track.manips',
                             ],
        ext_modules      = [Extension('track.pyrow', ['src/pyrow.c'])],
        scripts          = ['track/track'],
        install_requires = ['genomes'],
    )
