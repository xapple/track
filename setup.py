from distutils.core import setup

setup(
        name             =   'track',
        version          =   '1.0.0',
        description      =   'Python package for reading and writing genomic data',
        long_description =   open('README.md').read(),
        license          =   'GNU General Public License 3.0',
        url              =   'http://bbcf.epfl.ch/track',
        author           =   'EPFL BBCF',
        author_email     =   'webmaster.bbcf@epfl.ch',
        classifiers      =   ['Topic :: Scientific/Engineering :: Bio-Informatics'],
        packages         =   ['track',
                              'track.prase',
                              'track.serialize',
                              'track.transform',
                            ],
    )
