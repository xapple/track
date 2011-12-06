"""
This submodule enables you to read tracks into memory and to write tracks from memory using dictionaries. Doing this can quickly create memory problems, and is discouraged. However, if you know your track is not very large, and you want to load in the RAM, you can.
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
    """Loads a track from disk, whatever the format is and puts it in an enourmous dictionary. Contrary to most of the algorithms in this package, this method will load everything into the RAM. Be careful when using this method on large tracks.

       :param path: is the path to track file to create.
       :type  path: string
       :param format: is an optional parameter specifying the format of the track to create when it cannot be guessed from the file extension.
       :type  format: string
       :returns: a dictionary containing all features of every chromosome contained in a track.

       ::

            from track.memory import read, write
            genes = read('tracks/rp_genes.bed')
            print genes['chrX'][1523]
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

       :param dictionary: contains the chromosomes and features.
       :type  dictionary: dict
       :param format: is the path to track file to write to.
       :type  format: string
       :param format: is an optional parameter specifying the format of the track to create when it cannot be guessed from the file extension.
       :type  format: string
       :returns: None

       ::

            from track.memory import read, write
            genes = read('tracks/rp_genes.gff')
            genes['chrX'][1523] = (183, 195, 'bra', 1.9)
            write('tracks/modified.bed', genes)
    """
    # Guess the format #
    if not format: format = os.path.splitext(path)[1][1:]
    check_path(path)
    # Do the job #
    serializer = get_serializer(path, format)
    parser     = get_parser(dictionary, 'memory')
    return parser(serializer)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
