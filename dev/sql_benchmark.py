# Modules #
import sqlite3, os, timeit, random, tempfile
from track.common import Timer

# Variables #
global num_entries
num_entries = 1000000

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
    os.remove(path)

def reopen_database(path):
    global connection, cursor
    cursor.close()
    connection.close()
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

def generate_data():
    global num_entries
    name_gen = tempfile._RandomNameSequence()
    for i in range(num_entries):
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

################################################################################
# Read functions #
def read_one_by_one(command):
    cursor.execute(command)
    sum = 0
    while True:
        try:
            x = cursor.fetchone()
            sum += x[2]
        except TypeError as err:
            break

def read_all(command):
    cursor.execute(command)
    sum = 0
    data = cursor.fetchall()
    data = list(data)
    for x in data:
        sum += x[2]

def read_iterator(command):
    cursor.execute(command)
    sum([x[2] for x in cursor])

################################################################################
# Write #
path = "test_database.sql"
data = list(generate_data())

print "--- Write ---"
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
with Timer('read_one_by_one'): read_one_by_one(data)

reopen_database(path)
with Timer('read_all'): read_all(data)

reopen_database(path)
with Timer('read_iterator'): read_iterator(data)

cursor.close()
connection.close()
destroy_database(path)
