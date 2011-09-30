"""
Common stuff for python projects.
"""

###############################################################################
def iterate_lines(path, comment_char="#", linebreak_char=r"\\"):
    """
    Iterate over the lines of a text file in an intelligent way.
    1) Empty lines are skipped.
    3) Lines starting with comments characters such as '#' are skipped.
    2) Lines ending with line break characters such as '\\' are assembled.
    This function yields the line number and the line content as a tuple.
    """
    # The pieces of a file are every block of data separated by the newline character.
    # The units of the file are composed by taking the pieces and removing empty and comment lines.
    # The actual lines of the file are composed by taking the units and joining line breaks.
    def units(iterable):
        for number, piece in enumerate(iterable):
            piece = piece.strip()
            if len(piece) == 0: continue
            if piece.startswith(comment_char): continue
            yield number, piece
    def lines(iterable):
        for number, unit in iterable:
            while unit.endswith(linebreak_char):
                unit = unit.strip(linebreak_char)
                unit += iterable.next()[1]
            yield number, unit
    with open(path, 'r') as file:
        for line in lines(units(file)): yield line

################################################################################
def make_file_names(path):
    """
    Given a path to a file, generate more filenames.

    >>> g = make_file_names("tmp/test.png")
    >>> g.next()
    'tmp/test.png'
    >>> g.next()
    'tmp/test_1.png'
    >>> g.next()
    'tmp/test_2.png'
    """
    yield path
    import sys, os
    constant, ext = os.path.splitext(path)
    for i in xrange(1,sys.maxint): yield constant + "_" + str(i) + ext

################################################################################
def check_path(path):
    """
    Raise an exception if the path *path* is already taken.
    """
    import os
    if os.path.exists(path): raise Exception("The location '" + path + "' is already taken")

################################################################################
def check_executable(tool_name):
    """
    Raises an exception if the executable *tool_name* is not found.
    """
    import subprocess
    try:
        subprocess.Popen([tool_name], stderr=subprocess.PIPE)
    except OSError:
         raise Exception("The executable '" + tool_name + "' cannot be found")

################################################################################
def natural_sort(item):
    """
    Sort strings that contain numbers correctly.

    >>> l = ['v1.3.12', 'v1.3.3', 'v1.2.5', 'v1.2.15', 'v1.2.3', 'v1.2.1']
    >>> l.sort(key=natural_sort)
    >>> l.__repr__()
    "['v1.2.1', 'v1.2.3', 'v1.2.5', 'v1.2.15', 'v1.3.3', 'v1.3.12']"
    """
    import re
    def try_int(s):
        try: return int(s)
        except ValueError: return s
    return map(try_int, re.findall(r'(\d+|\D+)', item))

################################################################################
def temporary_path(suffix=''):
    """
    Often, one needs a new random and temporary file path
    instead of the random and temporary file object provided
    by the 'tempfile' module.
    """
    import tempfile
    file = tempfile.NamedTemporaryFile(suffix=suffix)
    path = file.name
    file.close()
    return path

################################################################################
def sentinelize(iterable, sentinel):
    """
    Add an item to the end of an iterable.

    >>> list(sentinelize(range(4), 99))
    [0, 1, 2, 3, 99]
    """
    for item in iterable: yield item
    yield sentinel

################################################################################
def sqlcmp(file_a, file_b):
    """
    Compare two two sqlite3 databases via their dumps.
    """
    import itertools, sqlite3
    A = sqlite3.connect(file_a)
    B = sqlite3.connect(file_b)
    for a,b in itertools.izip_longest(A.iterdump(), B.iterdump()):
        if a != b: return "A: " + a + "\nB:" + b
    return True

################################################################################
def empty_sql_file(path):
    """
    Create an empty sql file at the path specified.
    """
    import sqlite3
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    cursor.close()
    connection.close()

################################################################################
def empty_file(path):
    """
    Create an empty sql file at the path specified.
    """
    with open(path, 'w') as f: pass

################################################################################
def int_to_roman(input):
    """
    Convert an integer to a roman numeral.

    >>> int_to_roman(1999)
    'MCMXCIX'
    """
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    if type(input) != type(1): raise TypeError, 'Expected integer, got "%s."' % type(input)
    if not 0 < input < 4000: raise ValueError, 'Argument must be between 1 and 3999.'
    result = ""
    for i in range(len(ints)):
       count   = int(input / ints[i])
       result += nums[i] * count
       input  -= ints[i] * count
    return result

################################################################################
def roman_to_int(input):
    """
    Convert a roman numeral to an integer.

    >>> orig_integers = range(1, 4000)
    >>> romans = [int_to_roman(i) for i in orig_integers]
    >>> computed_integers = [roman_to_int(r) for r in romans]
    >>> print orig_integers == computed_integers
    True
    """
    ints = [1000, 500, 100, 50,  10,  5,   1]
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    if type(input) != type(""): raise TypeError, 'Expected string, got "%s."' % type(input)
    input = input.upper()
    places = []
    for c in input:
        if not c in nums:
            raise ValueError, 'Input is not a valid roman numeral: "%s."' % input
    for i in range(len(input)):
        c = input[i]
        value = ints[nums.index(c)]
        try:
            nextvalue = ints[nums.index(input[i +1])]
            if nextvalue > value: value *= -1
        except IndexError: pass
        places.append(value)
    output = sum([n for n in places])
    if int_to_roman(output) == input: return output
    else: raise ValueError, 'Input is not a valid roman numeral: "%s."' % input

################################################################################
terminal_colors = {
    'end':    '\033[0m',    # Text Reset
    'blink':  '\033[5m',    # Blink
    'txtblk': '\033[0;30m', # Black - Regular
    'txtred': '\033[0;31m', # Red
    'txtgrn': '\033[0;32m', # Green
    'txtylw': '\033[0;33m', # Yellow
    'txtblu': '\033[0;34m', # Blue
    'txtpur': '\033[0;35m', # Purple
    'txtcyn': '\033[0;36m', # Cyan
    'txtwht': '\033[0;37m', # White
    'bldblk': '\033[1;30m', # Black - Bold
    'bldred': '\033[1;31m', # Red
    'bldgrn': '\033[1;32m', # Green
    'bldylw': '\033[1;33m', # Yellow
    'bldblu': '\033[1;34m', # Blue
    'bldpur': '\033[1;35m', # Purple
    'bldcyn': '\033[1;36m', # Cyan
    'bldwht': '\033[1;37m', # White
    'unkblk': '\033[4;30m', # Black - Underline
    'undred': '\033[4;31m', # Red
    'undgrn': '\033[4;32m', # Green
    'undylw': '\033[4;33m', # Yellow
    'undblu': '\033[4;34m', # Blue
    'undpur': '\033[4;35m', # Purple
    'undcyn': '\033[4;36m', # Cyan
    'undwht': '\033[4;37m', # White
    'bnkblk': '\033[5;30m', # Black - Blinking
    'bnkred': '\033[5;31m', # Red
    'bnkgrn': '\033[5;32m', # Green
    'bnkylw': '\033[5;33m', # Yellow
    'bnkblu': '\033[5;34m', # Blue
    'bnkpur': '\033[5;35m', # Purple
    'bnkcyn': '\033[5;36m', # Cyan
    'bnkwht': '\033[5;37m', # White
    'bakblk': '\033[40m',   # Black - Background
    'bakred': '\033[41m',   # Red
    'bakgrn': '\033[42m',   # Green
    'bakylw': '\033[43m',   # Yellow
    'bakblu': '\033[44m',   # Blue
    'bakpur': '\033[45m',   # Purple
    'bakcyn': '\033[46m',   # Cyan
    'bakwht': '\033[47m',   # White
}

################################################################################
class JournaledDict(object):
    """
    A dictionary like object that tracks modification to itself.
    It has an extra special boolean self.modified value that starts off with "False"
    It has three special methods: self.save(), self.rollback() and self.overwrite()

       * rollback() will reset the self.modified variable to False and restore
    the dictionary to it's previous state.

       * save()  will reset the self.modified variable to False and remember
    the dictionary current's state.

       * overwrite(d) will reset the self.modified variable to True and repalce
    the dictionary with the one passed to it.
    """

    def __init__(self, d=None):
        # The dictionary itself #
        if d: self.data = d
        else: self.data = {}
        # The remembered state #
        self.backup = self.data.copy()
        # The boolean value #
        self.modified = False

    def __cmp__(self, d):
        if isinstance(d, JournaledDict): return cmp(self.data, d.data)
        else: return cmp(self.data, d)

    def __getitem__(self, key):
        if key in self.data: return self.data[key]
        if hasattr(self.__class__, "__missing__"): return getattr(self.__class__, "__missing__")(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.modified = True
        self.data[key] = item

    def __delitem__(self, key):
        self.modified = True
        del self.data[key]

    def __repr__(self): return repr(self.data)
    def __iter__(self): return iter(self.data)
    def __contains__(self, key): return key in self.data
    def __len__(self): return len(self.data)
    def keys(self): return self.data.keys()
    def items(self): return self.data.items()
    def iteritems(self): return self.data.iteritems()
    def iterkeys(self): return self.data.iterkeys()
    def itervalues(self): return self.data.itervalues()
    def values(self): return self.data.values()
    def has_key(self, key): return key in self.data
    def get(self, key, d=None): return self.data.get(key, d)

    #-----------------------------------------------------------------------------#
    def clear(self):
        self.modified = True
        self.data.clear()

    def setdefault(self, key, failobj=None):
        if key not in self:
            self.modified = True
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        self.modified = True
        return self.data.pop(key, *args)

    def popitem(self):
        self.modified = True
        return self.data.popitem()

    def copy(self):
        return JournaledDict(self.data.copy())

    def update(self, d=None, **kwargs):
        if d is None: return
        self.modified = True
        if isinstance(d, JournaledDict): self.data.update(d.data)
        elif isinstance(d, dict) or not hasattr(d, 'items'): self.data.update(d)
        else:
            for k, v in d.items(): self[k] = v
        if len(kwargs): self.data.update(kwargs)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable: d[key] = value
        return d

    #-----------------------------------------------------------------------------#

    def save(self):
        self.modified = False
        self.backup = self.data.copy()

    def rollback(self):
        self.modified = False
        self.data = self.backup.copy()

    def overwrite(self, d):
        self.modified = True
        self.data = d
