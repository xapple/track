"""
Extra functionality that can be used by other libraries.
"""

# Internal modules #
import track
from track.util import add_chromsome_prefix
from track.common import natural_sort, collapse

################################################################################
class TrackCollection(object):
    """
    The TrackCollection class can be useful for grouping many
    Track objects together and represent them as one.
    """
    def __init__(self, tracks, fields_collapse=None, chroms_collapse=None):
        self.tracks = tracks
        self.fields_collapse = fields_collapse
        self.chroms_collapse = chroms_collapse

    def __iter__(self): return iter(self.chromosomes)
    def __contains__(self, key): return key in self.chromosomes
    def __len__(self): return len(self.chromosomes)
    def __nonzero__(self): return True
    def __repr__(self): return "TrackCollection containing %s" % self.tracks

    @property
    def chromosomes(self):
        if not hasattr(self.tracks[0], "chromosomes"): return []
        chroms = collapse(self.chroms_collapse, [t.chromosomes for t in self.tracks])
        chroms.sort(key=natural_sort)
        return chroms

    @property
    def name(self):
        plural = len(self.tracks) > 1
        return 'Collection of %i track%s' % (len(self.tracks), plural and 's' or '')

    @property
    def chrmeta(self):
        if not hasattr(self.tracks[0], "chrmeta"): return {}
        return dict([(chrom,meta) for chrom,meta in self.tracks[0].chrmeta if chrom in self])

    @property
    def datatype(self):
        for t in self.tracks:
            if t.datatype: return t.datatype

    @property
    def assembly(self):
        for t in self.tracks:
            if t.assembly: return t.assembly

    @property
    def fields(self):
        return collapse(self.fields_collapse, [t.fields for t in self.tracks])

    @fields.setter
    def fields(self, value):
        for t in self.tracks: t.fields = value

    def read(self, *args, **kwargs):
        return [t.read(*args, **kwargs) for t in self.tracks]

    def close(self):
        for t in self.tracks: t.close()

################################################################################
class VirtualTrack(object):
    """
    The VirtualTrack class is a promise of a track to come in the future. The VirtualTrack
    has methods similar to the real Track. You can query its *fields* attribute and read
    specific chromosomes. The thing is that the features don't exist until you try to read them.
    Only once you issue ``virtual_track.read('chr1')`` is the result computed just
    in time.
    """
    def __init__(self):
        self.promises = {}
        self.chrmeta = {}
        self.info = {}
        self.tracks_to_close = []

    def __iter__(self): return iter(self.chromosomes)
    def __contains__(self, key): return key in self.chromosomes
    def __len__(self): return len(self.chromosomes)
    def __nonzero__(self): return True

    @property
    def chromosomes(self):
        chroms = self.promises.keys()
        chroms.sort(key=natural_sort)
        return chroms

    @property
    def datatype(self):
        return self.info.get('datatype', None)

    @datatype.setter
    def datatype(self, value):
        self.info['datatype'] = value

    @property
    def name(self):
        return self.info.get('name', 'Unnamed')

    @name.setter
    def name(self, value):
        self.info['name'] = value

    @property
    def assembly(self):
        return self.info.get('assembly', None)

    @assembly.setter
    def assembly(self, value):
        self.info['assembly'] = value

    def write(self, chromosome, stream):
        self.promises[chromosome] = stream

    def read(self, chromosome=None):
        # If we have a specific chromosome #
        if chromosome: return self.promises[chromosome]
        # Else we want all the chromosomes at once #
        return self.read_all()

    def read_all(self):
        for chrom in self:
            for f in add_chromsome_prefix(chrom, self.read(chrom)): yield f

    def export(self, path, format=None):
        with track.new(path, format) as t:
            for chrom in self: t.write(chrom, self.read(chrom))
            t.chrmeta = self.chrmeta
            t.info    = self.info
        self.close()

    def close(self):
        for t in self.tracks_to_close: t.close()
