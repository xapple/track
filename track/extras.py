"""
Extra functionality that can be used by other libraries.
"""

################################################################################
class TrackCollection(object):
    """
    The TrackCollection class can be useful for grouping many Track objects together and represent them as one.
    """
    def __init__(self, tracks):
        self.tracks      = tracks
        self.name        = 'Collection of ' + str(len(tracks)) + ' track' + ((len(tracks) > 1) and 's' or '')
        self.chromosomes = list(reduce(set.intersection, [set(list(t)) for t in tracks]))
        self.chrmeta     = tracks[0].chrmeta

    def __iter__(self): return iter(self.chromosomes)
    def __contains__(self, key): return key in self.chromosomes
    def __len__(self): return len(self.chromosomes)

    def read(self, *args, **kwargs): return [t.read(*args, **kwargs) for t in self.tracks]


################################################################################
class VirtualTrack(object):
    """
    The VirtualTrack class is a promise of a track to come in the future. The VirtualTrack
    has methods similar to the real Track. You can query its *fields* attribute and read
    specific chromosomes. The thing is that the features don't exist until you try to read them.
    Only once you issue ``virtual_track.read('chr1')`` is the result comupted just
    in time.
    """
    def __init__(self, tracks):
        pass

    def read(self, chrom):
        pass
