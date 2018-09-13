import load_xml as lx
# import string
from sys import argv
import os
import commands

funcs = []
sock_path = ""
global path

def help(arg):
    print "need xml path"


def to_h_define(namespace):
    return "__H_" + namespace.upper() + "_EVENT"


def show_h_begin(namespace):
    head_org = commands.getoutput("cat "+path+"head.h.org")
    print "#ifndef " + to_h_define(namespace) + "\n\
#define " + to_h_define(namespace) + "\n\
\n\
#include \"string\"\n\
#include \"list\"\n\
#include \"vector\"\n\
#include \"map\"\n\
#include <iostream>\n\
#include <boost/bind.hpp>\n\
#include <boost/thread.hpp>\n\
#include <boost/asio.hpp>\n\
#include <boost/enable_shared_from_this.hpp>\n\
#include <rapidjson/document.h>\n\
#include <rapidjson/stringbuffer.h>\n\
#include <rapidjson/writer.h>\n\
#include <json_obj.h>\n\
\n\
\n\
#ifndef IN\n\
#define IN\n\
#endif\n\
#ifndef OUT\n\
#define OUT\n\
#endif\n\
#ifndef INOUT\n\
#define INOUT\n\
#endif\n\
\n\
namespace " + namespace + "\n" + head_org;


def show_h_end(namespace):
    print "};\n\
\n\
} //namespace\n\
\n\
using namespace " + namespace + ";\n\
\n\
#endif //METADATA_SERVER_H"


type_tab = {
    "in": "IN",
    "out": "OUT",
    "in/out": "INOUT"
}

param_tab = {
    "string": " string & ",
    "int": " int & ",
    "uint": " unsigned int & ",
    "long": " long & ",
    "ulong": " unsigned long & ",
    "bool": " bool & ",
    "list_string": " list<string> &",
    "vec_string": " vector<string> &",
    "map_string": " map<string,string> &",
    "json": " json_obj &"
}


def gen_param(param):
    res_str = type_tab[param["param_type"]]
    res_str += param_tab[param["param_value"]]
    res_str += param["param_name"] + ","
    return res_str


def gen_params(func):
    res_str = ""
    if len(func["params"]) == 0: return ""
    for param in func["params"]:
        res_str += gen_param(param)
    res_str = res_str[0:len(res_str) - 1]
    return res_str


def gen_func(func):
    res_str = "\tvirtual int "
    res_str += func["func_name"]
    res_str += "("
    res_str += gen_params(func)
    res_str += "){cout<<\"" + func["func_name"] + "\"<<endl;return 0;}"
    res_str += "\n"
    return res_str


def gen_funcs():
    res_str = ""
    for func in funcs:
        res_str += gen_func(func)
    return res_str


if __name__ == '__main__':
    path = os.path.abspath(argv[0])
    path = os.path.dirname(path) + '/'
    if (len(argv) < 2):
        help(argv)
        exit(1)
    funcs, sock, client, server = lx.load_xml(argv[1])
    sock_path = sock["name"]
    namespace = server["namespace"]
    show_h_begin(namespace)
    print gen_funcs()
    show_h_end(namespace)
