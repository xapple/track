from distutils.core import setup, Extension

setup(
        name             =   'track',
        version          =   '1.1.0',
        description      =   'Python package for reading and writing genomic data',
        long_description =   open('README.md').read(),
        license          =   'GNU General Public License 3.0',
        url              =   'http://bbcf.epfl.ch/track',
        author           =   'EPFL BBCF',
        author_email     =   'webmaster.bbcf@epfl.ch',
        classifiers      =   ['Topic :: Scientific/Engineering :: Bio-Informatics'],
        packages         =   ['track',
                              'track.parse',
                              'track.serialize',
                              'track.test',
                              'track.manips',
                             ],
        package_data     = {'track': ['genomes.db']},
        ext_modules      = [Extension('track.pyrow', ['src/pyrow.c'])],
        scripts          = ['track/track'],
    )
