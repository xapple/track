"""
This subpackage contains functions to access the GenRep server.

Example usage:

    >>> from track import genrep
    >>> print genrep.assemblies
    [{u'source_name': u'UCSC', u'name': u'ce6', u'created_at': u'2010-12-19T20:52:31Z', u'updated_at': u'2011-01-05T14:58:43Z', u'bbcf_valid': True, u'nr_assembly_id': 106, u'source_id': 4, u'genome_id': 8, u'id': 14, u'md5': u'fd56 ......

    >>> print genrep.assemblies.by('name')
    ['ce6', 'danRer7', 'dm3', 'GRCh37', 'hg19', 'MLeprae_TN', ......

    >>> print genrep.assemblies.get('hg19')
    {u'bbcf_valid': True, u'created_at': u'2010-12-16T16:08:13Z', u'genome_id': 5, u'id': 11, ......

    >>> print genrep.assemblies.filter('genome_id', 5)
    [{u'bbcf_valid': False, u'created_at': u'2011-03-25T01:56:41Z', u'genome_id': 5, u'id': 22, ......

    >>> print genrep.assemblies.hg19.id
    11

    Same goes for organisms, genomes, etc.

    >>> from track.genrep import get_assembly
    >>> a = get_assembly('hg19')
    >>> print a.created_at
    '2010-12-16T16:08:13Z'

    >>> print [c['name'] for c in a.chromosomes]
    [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', ......

    >>> from track.genrep import guess_specie
    >>> print guess_specie(['chr1, 'chr2', 'chr3', 'chr4', 'chr5', 'chrC', 'chrM'])
    arabidopsis
"""

# Built-in modules #
import urllib2, json

# Internal modules #
from track.common import JsonJit

# Constants #
url = "http://bbcftools.vital-it.ch/genrep/"

################################################################################
def is_up(self):
    """Check if GenRep webservice is available"""
    try: urllib2.urlopen(self.url + "/nr_assemblies.json", timeout=2)
    except urllib2.URLError: return False
    return True

def get_assembly(name):
    """Creates an Assembly object"""
    # Check for HTTP errors #
    try: assembly = Assembly(name)
    except urllib2.URLError: return None
    # Check for empty JSON #
    if not assembly.json: return None
    # Return the assembly #
    return assembly

def guess_specie(list_of_chr_names):
    """Takes a list of chromosome names
       and tries to guess the specie."""
    #TODO

################################################################################
class Assembly(object):
    """Get an Assembly object corresponding to *assembly*.

    *assembly* may be an integer giving the assembly ID,
               or a string giving the assembly name,
               or a dictionary describing the species
               or an object describing the species.
    """

    def __init__(self, assembly):
        # Can be string or URL #
        if isinstance(assembly, int):          suffix = "id=%s"  % assembly
        elif isinstance(assembly, basestring): suffix = "name=%s"  % assembly
        elif isinstance(assembly, dict):       suffix = "name=%s"  % assembly['name']
        else:                                  suffix = "name=%s"  % assembly.name
        # Download data #
        info  = json.loads(urllib2.urlopen(url + "assemblies.json?assembly_"  + suffix).read())
        chrom = json.loads(urllib2.urlopen(url + "chromosomes.json?assembly_" + suffix).read())
        # Update the self attributes with info data #
        self.json = info[0]['assembly']
        self.__dict__.update(self.json)
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

################################################################################
# Expose base resources #
organisms     = JsonJit(url + "organisms.json",     'organism')
genomes       = JsonJit(url + "genomes.json",       'genome')
nr_assemblies = JsonJit(url + "nr_assemblies.json", 'nr_assembly')
assemblies    = JsonJit(url + "assemblies.json",    'assembly')
sources       = JsonJit(url + "sources.json",       'source')
