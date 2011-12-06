"""
This subpackage enables you to load genomic files without
converting them into SQLite format.

Indeed, when loading a file, instead of completely parsing the genomic file,
these modules will only return a generator ready to run. This avoids creating
an SQLite file, but should be used only if your genomic file is already
sorted by chromosome, by start position and by end position.
Also, multi-track files are not supported.
"""

# Built-in modules #
import sys, gzip

# Internal modules #
import track
from track import FeatureStream
from track.common import if_url_then_get_url, is_gzip, check_file
from track.util import determine_format, parse_header_line

# Variables #
generators = {
    'bed':      {'module': 'track.simple.bed',      'class': 'SimpleBED'},
    'wig':      {'module': 'track.simple.wig',      'class': 'SimpleWIG'},
    'bedGraph': {'module': 'track.simple.bedGraph', 'class': 'SimpleBedGraph'},
}

################################################################################
def load(path, format=None):
    """
    Loading a track with this function will return a SimpleTrack object.

    The SimpleTrack is missing all the methods such as *read*, *search*, etc.
    However it can be iterated on. Doing so will return as many tuples as
    there are chromosomes in the file. A tuple will contain the name of the current
    chromosome, and a FeatureStream yielding features.

    :param path: is the path to track file to load or an URL. If the path is an URL, the file will be downloaded automatically. If the path is a GZIP file, it will be decompressed automatically.
    :type  path: string
    :param format: is an optional parameter specifying the format of the track to load when it cannot be guessed from the file extension.
    :type  format: string
    :returns: a SimpleTrack instance

    ::

        from track.simple import load
        with load("/tracks/rp_genes.bed") as t:
            print t.next()
            # ('chr1', <FeatureStream object at 0x109799190>)
            print t.next()
            # ('chr2', <FeatureStream object at 0x1097caa50>)

    ::

        from track.simple import load
        all_features = []
        with load("/tracks/scores.wig") as t:
            for chrom, data in t:
                for feature in data:
                    all_features.append([chrom] + feature)
    """
    # Check if URL #
    path = if_url_then_get_url(path)
    # Check not empty #
    check_file(path)
    # Guess the format #
    if not format: format = determine_format(path)
    # If sql, just make a track with the main module #
    if format == 'sql': return track.load(path, format, readonly)
    # Is the format supported ? #
    if not format in generators: raise Exception("The format '%s' is not supported." % format)
    info = generators[format]
    # Import the objects #
    base_module    = __import__(info['module'])
    sub_module     = sys.modules[info['module']]
    class_object   = getattr(sub_module, info['class'])
    class_instance = class_object(path)
    # Set the format #
    class_instance.format = format
    # Return an instance #
    return class_instance

################################################################################
class SimpleTrack(object):
    """
    Works only with generators. Can only read the track once. No going back.
    """

    def __init__(self, path, readonly=False, autosave=True, orig_path=None, orig_format=None):
        # Check the path #
        self.path = path
        check_file(path)
        # Open the file #
        if is_gzip(path): self.file = gzip.open(path, 'r')
        else:             self.file = open(path, 'r')
        # Simulate Track attributes #
        self.info = parse_header_line(self.file)
        self.fields = self.guess_fields()

    def __enter__(self):
        """Called when evaluating the 'with' statement."""
        return self

    def __exit__(self, errtype, value, traceback):
        """Called when exiting the 'with' statement."""
        self.file.close()

    def __nonzero__(self):
        """Called when evaluating ``if t: pass``."""
        return True

    def __iter__(self):
        """Called when evaluating ``for chrom, data in t: pass``."""
        return self.stream_generator()

    def stream_generator(self):
        global chrom, feature
        cur_chrom = ''
        feat_gen  = self.read_features()
        chrom, feature = feat_gen.next()
        def iter_until_different_chr():
            global chrom, feature
            while True:
                if chrom != cur_chrom: break
                yield feature
                chrom, feature = feat_gen.next()
        while True:
            if chrom == cur_chrom: break
            cur_chrom = chrom
            yield cur_chrom, FeatureStream(iter_until_different_chr(), self.fields)

    @property
    def modified(self):
        return False

    @property
    def assembly(self):
        pass

    @assembly.setter
    def assembly(self, value):
        pass

    def error(self, message, path=None, line_number=None):
        if path and line_number:       location = " '%s:%s'" % (path, line_number)
        elif path and not line_number: location = " '%s'"    % (path)
        else:                          location = ""
        raise Exception(message % location)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
