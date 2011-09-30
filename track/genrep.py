"""
This subpackage contains functions to access the GenRep server.

Example usage:

    >>> from track.genrep import Assembly
    >>> a = Assembly('hg19')
    >>> print a.created_at
    '2010-12-16T16:08:13Z'

    >>> print [c['name'] for c in a.chromosomes]
    [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', ......
"""

# Built-in modules #
import urllib2, json

# Constants #
url = "http://bbcftools.vital-it.ch/genrep/"

################################################################################
def is_up(self):
    """Check if GenRep webservice is available"""
    try: urllib2.urlopen(self.url + "/nr_assemblies.json", timeout=2)
    except urllib2.URLError: return False
    return True

################################################################################
class Assembly(object):
    """Get an Assembly object corresponding to *assembly*.

    *assembly* may be an integer giving the assembly ID,
               or a string giving the assembly name,
               or a dictionary describing the species
               or an object describing the species.
    """

    def __init__(self, assembly):
        # Called must check if success is true #
        self.success = True
        # Can be string or URL #
        if isinstance(assembly, int):          suffix = "id=%s"  % assembly
        elif isinstance(assembly, basestring): suffix = "name=%s"  % assembly
        elif isinstance(assembly, dict):       suffix = "name=%s"  % assembly['name']
        else:                                  suffix = "name=%s"  % assembly.name
        # Download data #
        try:
            info  = json.loads(urllib2.urlopen(url + "assemblies.json?assembly_"  + suffix).read())
            chrom = json.loads(urllib2.urlopen(url + "chromosomes.json?assembly_" + suffix).read())
        except urllib2.URLError:
            self.success = False
        # Is empty if assembly not available #
        if not info: self.success = False
        else: self.__dict__.update(info[0]['assembly'])
        # Update the self.chromosome with chromosome data #
        self.chromosomes = [item['chromosome'] for item in chrom]

    @property
    def chrmeta(self):
        """ Returns a dictionary of chromosome meta data looking something like:

            {'chr1': {'length': 249250621},
             'chr2': {'length': 135534747},
             'chr3': {'length': 135006516},

        """
        return dict([(v['name'].encode('ascii'), dict([('length', v['length'])])) for v in self.chromosomes])
