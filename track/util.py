"""
Usefull stuff for the track package.
"""

# Built-in modules #
import os, shlex

# Internal modules #
from track.common import temporary_path, iterate_lines

###############################################################################
# Constants #
sql_field_types = {'start':        'integer',
                   'end':          'integer',
                   'score':        'real',
                   'strand':       'integer',
                   'name':         'text',
                   'thick_start':  'integer',
                   'thick_end':    'integer',
                   'item_rgb':     'text',
                   'block_count':  'integer',
                   'block_sizes':  'text',
                   'block_starts': 'text',
                   'attributes':   'text',
                   'source':       'text',
                   'frame':        'integer',
                   'attributes':   'text',}

py_field_types  = {'start':        int,
                   'end':          int,
                   'score':        float,
                   'strand':       int,
                   'name':         str,
                   'thick_start':  int,
                   'thick_end':    int,
                   'item_rgb':     str,
                   'block_count':  int,
                   'block_sizes':  str,
                   'block_starts': str,
                   'attributes':   str,
                   'source':       str,
                   'frame':        int,
                   'attributes':   str,}

format_synonyms = {'db': 'sql',
                   'bw': 'bigwig',
                   'bwg': 'bigwig',
                   'wiggle_0': 'wig',}

###############################################################################
def determine_format(path):
    """Try to guess the format of a track given its path.
       Returns a three letter extension."""
    # Get the extension #
    ext = os.path.splitext(path)[1][1:].lower()
    # An extension is provided #
    if ext: return format_synonyms.get(ext, ext)
    # Does the file exist #
    if not os.path.exists(path):
        raise Exception("The format of the path '%s' cannot be determined. Please specify a format or add an extension." % path)
    # Try our own sniffing now #
    with open(path, 'r') as file:
        file_format = guess_file_format(file)
    # If still nothing, raise exception #
    if not file_format:
        raise Exception("The format of the file '%s' cannot be determined. Please specify a format or add an extension." % path)
    # Return the format #
    file_format = file_format.lower()
    return format_synonyms.get(file_format, file_format)

###############################################################################
def guess_file_format(handle):
    """Try to guess the format of a track given its content.
       Returns a three letter extension."""
    # Check SQLite #
    if handle.read(15) == "SQLite format 3": return 'sql'
    handle.seek(0)
    # Try to read the track line #
    for number, line in enumerate(handle):
        line = line.strip("\n").lstrip()
        if number > 100: break
        if line.startswith("track "):
            try: id = dict([p.split('=',1) for p in shlex.split(line[6:])]).get('type', '')
            except ValueError: id = ''
            return id

###############################################################################
def gzip_inner_format(path):
    """Try to guess the format of a file inside a
       compressed gzip archive. Returns a three
       letter extension"""
    # Get the extension #
    ext = os.path.splitext(path.strip('.gz').strip('.gzip'))[1][1:]
    # An extension is provided #
    if ext: return format_synonyms.get(ext, ext)
    # Try our own sniffing now #
    import gzip
    file = gzip.open(path, 'r')
    file_format = guess_file_format(file)
    file.close()
    # If still nothing, raise exception #
    if not file_format:
        raise Exception("The inner format of the gzip file '%s' cannot be determined. Please specify a format or add an extension." % path)
    # Return the format #
    return format_synonyms.get(file_format, file_format)

###############################################################################
def parse_chr_file(self, path):
    """Read a chromsome file and return a dictionary"""
    chrmeta = {}
    for number, line in iterate_lines(path):
        items = line.split('\t')
        if len(items) == 1: items = line.split()
        if len(items) != 2:
            raise Exception("The file '" + path + ":" + str(number) + "' does not seam to be a valid chromosome file.")
        name = items[0]
        try:
            length = int(items[1])
        except ValueError:
            raise Exception("The file '" + path + ":" + str(number) + "' has non-integer as chromosome lengths.")
        chrmeta[name] = dict([('length', length)])
    if not chrmeta:
        raise Exception("The file '" + path + "' does not seam to contain any information.")
    return chrmeta

###############################################################################
def serialize_chr_file(chrmeta, path=None, seperator='\t'):
    """Read a dictionary and create a plain text file"""
    if not path: path = temporary_path()
    def lines():
        for k,v in chrmeta.items(): yield k + seperator + str(v['length']) + '\n'
    with open(path, 'w') as f: f.writelines(lines())
    return path

###############################################################################
def parse_header_line(handle):
    """
    Tries to parse the 'track' header line and returns a dictionary.
    For instance for the following line:
        track type=wiggle_0 name="DNA Footprints" source="University of Washington"
    You will get the following dictionary:
        {'name': 'DNA Footprints', 'source': 'University of Washington', 'type': 'wiggle_0'}
    """
    result = {}
    for line in handle:
        line = line.strip()
        if len(line) == 0:              continue
        if line.startswith("#"):        continue
        if line.startswith("browser "): continue
        if line.startswith("track "):
            try: result = dict([p.split('=',1) for p in shlex.split(line[6:])])
            except ValueError: pass
        break
    handle.seek(0)
    return result

################################################################################
def add_chromsome_prefix(sel, data):
    """Add the chromosome in front of every feature"""
    if type(sel) == str: chrom = (sel,)
    else:                chrom = (sel['chr'],)
    for f in data: yield chrom + tuple(f)

################################################################################
def join_read_queries(track, selections, fields):
    """Join read results when selection is a list"""
    for sel in selections:
        for f in add_chromsome_prefix(sel, track.read(sel, fields)): yield f

################################################################################
def make_cond_from_sel(selection):
    """Make an SQL condition string from a selection dictionary"""
    query = ""
    # Case start #
    if "start" in selection:
        query += "end > " + str(selection['start'])
        if selection.get('inclusion') == 'strict': query += " and start >= " + str(selection['start'])
    # Case end #
    if "end" in selection:
        if query: query += " and "
        query += "start < " + str(selection['end'])
        if selection.get('inclusion') == 'strict': query += " and end <= " + str(selection['end'])
    # Case strand #
    if "strand" in selection:
        if query: query += " and "
        query += 'strand == ' + str(selection['strand'])
    # Case score #
    if "score" in selection:
        if not isinstance(selection['score'], tuple): raise Exception("Score intervals must be tuples of size 2")
        if query: query += " and "
        query += 'score >= ' + str(selection['score'][0]) + ' and score <= ' + str(selection['score'][1])
    return query

################################################################################
def strand_to_int(strand):
    if strand == '+': return 1
    if strand == '-': return -1
    return 0

def int_to_strand(num):
    num = int(num)
    if num == 1: return  '+'
    if num == -1: return '-'
    return '.'

################################################################################
def floats_eq(a,b, epsilon=0.000001):
    """
    Return true if two floats are equals
    """
    return abs(a-b) < epsilon

def overlapping(start1, stop1, start2, stop2):
    """
    Return true if the two features 1 & 2 are overlapping.
    """
    return start1 <= stop2 and stop1 >= start2

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
