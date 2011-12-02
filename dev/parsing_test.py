"""
An optional test that is not run with the usual test suite. It evaluates the robustness of the text track parsers.
"""

# Built-in modules #
import os, re

# Internal modules #
import track
from track.test import challanges

################################################################################
def ext_to_clr(ext):
    """Extension to color number"""
    return str({'bed':6,'wig':4,'bedgraph':5}[ext])

def message(path, name, status, expected, text=None):
    """Function used to produce nice color output"""
    if text: text = re.sub(" '" + path, "", text)
    if text: text = text.replace("\n"," ")
    title, extension = name.split('.')
    if expected=='pass': s = ('\033[1;37;4'+ ext_to_clr(extension) + 'm' + extension + '\033[0m' + ': ' + title).ljust(42)
    else:                s = ('\033[1;30;4'+ ext_to_clr(extension) + 'm' + extension + '\033[0m' + ': ' + title).ljust(42)
    if status==expected:
        s += '\033[0;37m\033[42m passed the test \033[0m'
        if text: s += ' \033[2;37m' + text + '\033[0m'
    else:
        s += '\033[1;37m\033[41m\033[5;37m failed the test \033[0m'
        if text: s += ' \033[1;33m' + text + '\033[0m'
    print s

def run(create_sql_files=False):
    for format, outcomes in challanges.items():
        for outcome, paths in outcomes.items():
            for path in paths:
                name = os.path.basename(path)
                dest = os.path.splitext(path)[0] + '.sql'
                if os.path.exists(dest): os.remove(dest)
                try:
                    track.convert(path, dest)
                except Exception as err:
                    message(path, name, 'fail', outcome, str(err)[0:160])
                else:
                    message(path, name, 'pass', outcome)
                finally:
                    if not create_sql_files and os.path.exists(dest): os.remove(dest)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
