"""
This module evaluates the performance of the built-in python sqlite3 pacakge.
One can compare the execution times when using the library in different ways.
"""

# Modules #
import sqlite3, os, timeit, random, tempfile

# Variables #
global num_entries, connection, cursor
num_entries = 1000000

################################################################################
# Classes #
class Timer(object):
    """Times a given code block. Use it like this:

            with Timer('my batch process'): batch_benchmark(args)

    """

    def __init__(self, name=None, entries=1):
        import timeit
        self.name = name
        self.entries = entries
        self.timer = timeit.default_timer

    def __enter__(self):
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        total_time = self.end - self.start
        entry_time = (1000000*total_time / self.entries)
        line1 = "%.6f seconds for %s" % (total_time, self.name or 'Unnamed')
        line2 = "(%.3f usec per entry)" % entry_time
        print line1, line2

################################################################################
# General Functions #
def setup_database(path, auto_commit=False):
    global connection, cursor
    if auto_commit: connection = sqlite3.connect(path, isolation_level=None) # commit all the time
    else:           connection = sqlite3.connect(path)                       # no commits ever (default)
    cursor = connection.cursor()
    cursor.execute('create table dummy (one text, two text, three integer)')
    connection.commit()

def destroy_database(path):
    if os.path.exists(path): os.remove(path)

def reopen_database(path, rows=None):
    global connection, cursor
    cursor.close()
    connection.close()
    connection = sqlite3.connect(path)
    if rows: connection.row_factory = rows
    cursor = connection.cursor()

def generate_data():
    global num_entries
    name_gen = tempfile._RandomNameSequence()
    for i in xrange(num_entries):
        yield (name_gen.next(), name_gen.next(), random.randint(1,1000))

def time_the_execution(command):
    global num_entries
    timeit_count = 1
    t = timeit.Timer(command)
    sec = t.timeit(timeit_count)
    string = "%.6f sec for " % sec + command.func.__name__
    print string.ljust(40) + "(%.3f usec per entry)" % (1000000*sec / num_entries)

################################################################################
# Write Fonctions #
def simple_execute(iterable):
    global connection, cursor
    for x in iterable:
        cursor.execute('insert into dummy values (?,?,?)', x)
    cursor.close()
    connection.commit()
    connection.close()

def batch_execute(iterable):
    global connection, cursor
    cursor.executemany('insert into dummy values (?,?,?)', iterable)
    cursor.close()
    connection.commit()
    connection.close()

def simple_variable_table(iterable):
    global connection, cursor
    table = 'dummy'
    for x in iterable:
        cursor.execute('insert into ' + table + ' values (?,?,?)', x)
    cursor.close()
    connection.commit()
    connection.close()

def batch_variable_table(iterable):
    global connection, cursor
    table = 'dummy'
    cursor.executemany('insert into ' + table + ' values (?,?,?)', iterable)
    cursor.close()
    connection.commit()
    connection.close()

def variable_fields(iterable):
    global connection, cursor
    fields = ['one','two','three']
    table = 'dummy'
    cursor.executemany('insert into ' + table + ' values (' + ','.join(['?' for x in range(len(fields))]) + ')', iterable)
    cursor.close()
    connection.commit()
    connection.close()

def bad_bad_execute(iterable):
    # Don't do this
    global connection, cursor
    for x in iterable:
        cursor.execute('insert into dummy values ("' +x[0]+ '","' +x[1]+ '",' +str(x[2])+ ')')
    cursor.close()
    connection.commit()
    connection.close()

def bad_execute_many(iterable):
    # Don't do this
    global connection, cursor
    for x in iterable:
        cursor.execute('insert into dummy values (?,?,?)', x)
    cursor.close()
    connection.commit()
    connection.close()

################################################################################
# Read functions #
def read_one_by_one(command):
    global connection, cursor
    cursor.execute(command)
    sum = 0
    while True:
        try:
            x = cursor.fetchone()
            sum += x[2]
        except TypeError as err:
            break

def read_all(command):
    global connection, cursor
    cursor.execute(command)
    sum = 0
    data = cursor.fetchall()
    data = list(data)
    for x in data:
        sum += x[2]

def read_iterator(command):
    global connection, cursor
    cursor.execute(command)
    sum([x[2] for x in cursor])

def read_row(command):
    global connection, cursor
    cursor.execute(command)
    sum([x['three'] for x in cursor])

################################################################################
# Write #
path = "test_database.sql"
data = list(generate_data())

print "--- Write ---"
destroy_database(path)
setup_database(path)
with Timer('simple_execute'): simple_execute(data)
destroy_database(path)

setup_database(path)
with Timer('batch_execute'): batch_execute(data)
destroy_database(path)

setup_database(path)
with Timer('simple_variable_table'): simple_variable_table(data)
destroy_database(path)

setup_database(path)
with Timer('batch_variable_table'): batch_variable_table(data)
destroy_database(path)

setup_database(path)
with Timer('variable_fields'): variable_fields(data)
destroy_database(path)

setup_database(path)
with Timer('bad_bad_execute'): bad_bad_execute(data)

# Read #
print "--- Read ---"
connection = sqlite3.connect(path)
cursor = connection.cursor()
command = "select * from dummy"

reopen_database(path)
with Timer('read_one_by_one'): read_one_by_one(command)

reopen_database(path)
with Timer('read_all'): read_all(command)

reopen_database(path)
with Timer('read_iterator'): read_iterator(command)

reopen_database(path, rows=sqlite3.Row)
with Timer('read_row'): read_row(command)

cursor.close()
connection.close()
destroy_database(path)

