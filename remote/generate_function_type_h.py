import load_xml as lx
# import string
from sys import argv
import os
import commands

ONE_TEB = "    "

funcs = []


def help(arg):
    print "need xml path"


def show_head(port):
    print "#ifndef _FUNCTION_TYPE_"+port+"_H"
    print "#define _FUNCTION_TYPE_"+port+"_H\n"


def show_client_func_type(funcs, port):
    print "enum client_function_callback_type_" + port
    print "{"
    for f in funcs:
        print ONE_TEB + "client_function_callback_type_" + port+ "_"  + f["func_name"] + ","

    print "};"


def show_server_func_type(funcs, port):
    print "enum server_function_callback_type_" + port
    print "{"
    for f in funcs:
        print ONE_TEB + "server_function_callback_type_" + port+ "_" + f["func_name"] + ","

    print "};"


def show_end():
    print "\n#endif"


def show_all(port,funcs):
    show_head(port)
    show_client_func_type(funcs,port)
    show_server_func_type(funcs,port)
    show_end()


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    show_all(port, funcs)
