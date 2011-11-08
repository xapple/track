# Modules #
import os, sys, timeit, tempfile, random
from pysqlite2 import dbapi2 as sqlite3
from inspect import getfile, currentframe
from IPython.kernel import client
from functools import partial

# Globals #
parallelize = True
name_gen = tempfile._RandomNameSequence()

# Multiengines #
def setup_mec(this_dir):
    ''' Manually start several <ipengine> and one <ipcontroller> first'''
    mec = client.MultiEngineClient()
    print mec.get_ids()
    mec.execute("import sys")
    mec.execute("sys.path.append('" + this_dir + "')")
    mec.execute("from make_db import *")
    return mec

# Functions #
def setup_connection(path):
    con = sqlite3.connect(db)
    cur = con.cursor()
    return con, cur
def create_table(cur, name):
    cur.execute('create table ' + name + '(one text, two text, three integer)') 
def batch_insert(cur, table, iterable):
    cur.executemany('insert into ' + table + ' values (?,?,?)', iterable)
def generate_data():
    for i in range(10000):
        yield (name_gen.next(), name_gen.next(), random.randint(1,1000))
def time_execution(command):
    print "%.6f seconds elapsed." % timeit.Timer(command).timeit(1)

# Execution #
def exec_general(tables, db):
    con, cur = setup_connection(db)
    for t in tables: batch_insert(cur, t, generate_data())
    con.commit()
    con.close()

# Main #
if __name__=='__main__':
    this_dir = '/'.join(os.path.abspath(getfile(currentframe())).split('/')[:-1])+'/'
    #db = this_dir + "read_database.sql"
    tables = ["table" + str(i) for i in range(10)]
    if parallelize:
        mec = setup_mec(this_dir)
        time_execution(partial(mec.map, lambda t: exec_general(t, "/home/sinclair/svn/gMiner/Testing/benchmarking/sql/read_database.sql"), tables))
    else:
        time_execution(partial(map, lambda t: exec_general(t, "/home/sinclair/svn/gMiner/Testing/benchmarking/sql/read_database.sql"), tables))
