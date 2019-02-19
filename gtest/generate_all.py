#!/usr/bin/python
import load_xml as lx
import os
from sys import argv
import gen_add_h as gah
import gen_new_h as gnh
import gen_add_cpp as gac
import gen_new_cpp as gnc
import commands


def save_to_file(file_name, contents):
    fh = open(file_name, 'w')
    fh.write(contents)
    fh.close()


def gen_h(project, suit_name, cases):
    filepath = "output/" + suit_name + ".h"
    tmppath = filepath + ".tmp"
    if (os.path.exists(filepath)):
        commands.getoutput("mv " + filepath + " " + tmppath)
        save_to_file(filepath, gah.show_all(tmppath, project, suit_name, cases))
        commands.getoutput("rm -f " + tmppath)
    else:
        save_to_file(filepath, gnh.show_all(project, suit_name, cases))


def gen_hs(project, suits):
    for suit in suits:
        gen_h(project,suit["name"],suit["cases"])

def gen_cpp(project, suit_name, cases):
    filepath = "output/" + suit_name + ".cpp"
    tmppath = filepath + ".tmp"
    if (os.path.exists(filepath)):
        commands.getoutput("mv " + filepath + " " + tmppath)
        save_to_file(filepath, gac.show_all(tmppath, suit_name, cases))
        commands.getoutput("rm -f " + tmppath)
    else:
        save_to_file(filepath, gnc.show_all(suit_name, cases))


def gen_cpps(project, suits):
    for suit in suits:
        gen_cpp(project,suit["name"],suit["cases"])


if __name__ == '__main__':
    if len(argv) < 2:
        print "need xml"
        exit(1)
    project, suits = lx.load_xml(argv[1])
    os.system("mkdir output -p")
    gen_hs(project, suits)
    gen_cpps(project, suits)
