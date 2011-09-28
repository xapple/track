"""
This module also enables you to read tracks into memory and to write track from memory using dictionaries. Doing this can quickly create memory problems, and is discouraged. However, if you know your track is not very large, and you want to load in memory, you can.
"""

# Built-in modules #
import os

# Internal modules #
from track.util import determine_format
from track.common import check_path
from track.parse import get_parser
from track.serialize import get_serializer

################################################################################
def read(path, format=None):
    """Loads a track from disk, whatever the format is and puts it in an enourmous dictionary. . dictionary. Contrary to most of the algorithms in this package, this method will load everything into memory. Be careful when using this method on large tracks

            * *path* is the path to track file to load.
            * *format* is an optional string specifying the format of the track to load when it cannot be guessed from the file extension.

        Examples::

            from track.memory import read, write
            genes = read('tracks/rp_genes.bed')
            print genes['chrX'][1523]

        ``read`` returns a dictionary containing all features of every chromosome contained in a track.
    """
    # Guess the format #
    if not format: format = determine_format(path)
    # Do the job #
    serializer = get_serializer(None, 'memory')
    parser     = get_parser(path, format)
    return parser(serializer)

################################################################################
def write(dictionary, path, format=None):
    """Write a dictionary to disk, whatever the format is.

            * *dictionary* contains the chromosomes and features.
            * *path* is the path to track file to write to.
            * *format* is an optional string specifying the format of the track to load when it cannot be guessed from the file extension.

        Examples::

            from track.memory import read, write
            genes = read('tracks/rp_genes.gff')
            genes['chrX'][1523] = (183, 195, 'bra', 1.9)
            write('tracks/modified.bed', genes)

        ``write`` returns nothing.
    """
    # Guess the format #
    if not format: format = os.path.splitext(path)[1][1:]
    check_path(path)
    # Do the job #
    serializer = get_serializer(path, format)
    parser     = get_parser(dictionary, 'memory')
    return parser(serializer)
