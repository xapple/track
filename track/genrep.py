"""
This subpackage contains functions to access the GenRep server.

Example usage:

    >> from track import genrep
    >> print genrep.assemblies
    [{u'source_name': u'UCSC', u'name': u'ce6', u'created_at': u'2010-12-19T20:52:31Z', u'updated_at': u'2011-01-05T14:58:43Z', u'bbcf_valid': True, u'nr_assembly_id': 106, u'source_id': 4, u'genome_id': 8, u'id': 14, u'md5': u'fd56 ......

    >> print genrep.assemblies.by('name')
    ['ce6', 'danRer7', 'dm3', 'GRCh37', 'hg19', 'MLeprae_TN', ......

    >> print genrep.assemblies.get('hg19')
    {u'bbcf_valid': True, u'created_at': u'2010-12-16T16:08:13Z', u'genome_id': 5, u'id': 11, ......

    >> print genrep.assemblies.filter('genome_id', 5)
    [{u'bbcf_valid': False, u'created_at': u'2011-03-25T01:56:41Z', u'genome_id': 5, u'id': 22, ......

    >> print genrep.assemblies.hg19.id
    11

    Same goes for organisms, genomes, etc.

    >> from track.genrep import get_assembly
    >> a = get_assembly('hg19')
    >> print a.created_at
    '2010-12-16T16:08:13Z'

    >> print [c['name'] for c in a.chromosomes]
    [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10', u'11', u'12', ......
"""

# Built-in modules #
import urllib2, json

# Internal modules #
from track.common import JsonJit

# Constants #
url = "http://bbcftools.vital-it.ch/genrep/"

################################################################################
def is_up():
    """Check if GenRep webservice is available"""
    try: urllib2.urlopen(url + "nr_assemblies.json", timeout=2)
    except urllib2.URLError: return False
    return True

def get_assembly(name):
    """Creates an Assembly object"""
    # Check for HTTP errors #
    try: assembly = Assembly(name)
    except urllib2.URLError: return None
    # Check for empty JSON #
    if not hasattr(assembly, 'json'): return None
    # Return the assembly #
    return assembly

def find_possible_assemblies(chromosome_name):
    """Returns a list of genome ids that the
       given chromosome can be found in."""
    info = json.loads(urllib2.urlopen(url + "chromosomes.json?identifier=" + chromosome_name).read())
    return [chrom['chromosome']['genome_id'] for chrom in info]

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
        if info:
            self.json = info[0]['assembly']
            self.__dict__.update(self.json)
        # Update the self.chromosome with chromosome data #
        if chrom:
            self.chromosomes = [item['chromosome'] for item in chrom]
        # Extra attributes #
        self._chrmeta = None

    def guess_chromosome_name(self, chromosome_name):
        """Searches the assembly for chromosome synoyn names,
           and return the cannoncial name of the chromosome.
           Returns None if the chromosome is not known about.
        """
        address = url + "chromosomes.json?assembly_id=" + str(self.id) + "&identifier=" + chromosome_name
        info = json.loads(urllib2.urlopen(address).read())
        if len(info) != 1: return None
        return info[0]['chromosome']['name']

    @property
    def chrmeta(self):
        """Returns a dictionary of chromosome metadata looking something like:

            {'chr1': {'length': 249250621},
             'chr2': {'length': 135534747},
             'chr3': {'length': 135006516},

        """
        if not self._chrmeta:
            self._chrmeta = dict([(chrom['name'].encode('ascii'), dict([('length', chrom['length'])])) for chrom in self.chromosomes])
        return self._chrmeta

################################################################################
# Expose base resources #
organisms     = JsonJit(url + "organisms.json",     'organism')
genomes       = JsonJit(url + "genomes.json",       'genome')
nr_assemblies = JsonJit(url + "nr_assemblies.json", 'nr_assembly')
assemblies    = JsonJit(url + "assemblies.json",    'assembly')
sources       = JsonJit(url + "sources.json",       'source')

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
