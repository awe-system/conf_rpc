import load_xml as lx
# import string
from sys import argv
import os

funcs = []
sock_path = ""
global path

def help(arg):
    print "need xml path"


def show_cpp_begin():

    os.system("echo \'#include \""+server["filename"] +".h\"\';cat "+path+"head.cpp.org")


def show_cpp_end():
    print"    } catch (int &err)"
    print"    {\n"
    print"        put_err(doc_out, err);\n"
    print"    }\n"
    print"    dumps(doc_out, output);\n"
    print"}\n"
    print"#ifdef TESTTRANSTER_THREAD\n"
    print"int main(){\
	    transfer_thread_handler handler;\
	    transfer_thread thread(&handler);\
	    getchar();\
	    return 0;}\n"
    print"#endif\n"


def gen_socketpath(sock_path, namespace):
    res = "namespace " + namespace + "{\n"
    res += "string socketpath ="
    res += "\"" + sock_path + "\";\n};"
    return res


def gen_param(param):
    res_str = param["param_name"] + ","
    return res_str


def gen_params(params):
    res_str = ""
    if len(params) == 0: return ""
    for param in params:
        res_str += gen_param(param)
    res_str = res_str[0:len(res_str) - 1]
    return res_str


param_tab = {
    "string": "                string ",
    "int": "                int ",
    "uint": "                unsigned int ",
    "long": "                long & ",
    "ulong": "                unsigned long ",
    "bool": "                bool ",
    "list_string": "                list<string> ",
    "vec_string": "                vector<string> ",
    "map_string": "                map<string,string> ",
    "json": "                json_obj "
}

get_tab = {
    "string": "                get_string",
    "int": "                   get_int",
    "uint": "                  get_uint",
    "long": "                  get_long",
    "ulong": "                 get_ulong",
    "bool": "                  get_bool",
    "list_string": "                get_string_list",
    "vec_string": "                get_string_vec",
    "map_string": "                get_string_map"
}


def gen_in_param(param):
    res_str = param_tab[param["param_value"]]
    res_str += param["param_name"] + ";\n"
    if param["param_type"] != "out":
        res_str += "                key = string(\"" + param["param_name"] + "\");\n"
        res_str += get_tab[param["param_value"]]
        res_str += "(doc_in,key," + param["param_name"] + ");\n"
    return res_str


def gen_in_params(params):
    res_str = ""
    if len(params) == 0: return ""
    for param in params:
        res_str += gen_in_param(param)
    return res_str


put_tab = {
    "string": "                put_string",
    "int": "                put_int",
    "uint": "                put_uint",
    "long": "                put_long",
    "ulong": "                put_ulong",
    "bool": "                put_bool",
    "list_string": "               put_string_list",
    "vec_string": "                put_string_vec",
    "map_string": "                put_string_map",
    "json": "                put_json_obj"
}


def gen_out_param(param):
    res_str = ""
    if param["param_type"] != "in":
        res_str += "                key = string(\"" + param["param_name"] + "\");\n";
        res_str += put_tab[param["param_value"]]
        res_str += "(doc_out,key," + param["param_name"] + ");\n"
    return res_str


def gen_out_params(params):
    res_str = ""
    if len(params) == 0: return ""
    for param in params:
        res_str += gen_out_param(param)
    return res_str


def gen_func(func, i):
    if i == 0:
        res_str = "        "
    else:
        res_str = "        else "
    res_str += "if(action == string(\""
    res_str += func["func_name"]
    res_str += "\")){\n"
    res_str += gen_in_params(func["params"])
    res_str += "                int thread_error = handler->"
    res_str += func["func_name"]
    res_str += "("
    res_str += gen_params(func["params"])
    res_str += ");\n"
    res_str += "                if(thread_error) throw thread_error;\n"
    res_str += "                put_err(doc_out, 0);\n"
    res_str += gen_out_params(func["params"])
    res_str += "        }\n"
    return res_str


def gen_funcs(funcs):
    res_str = ""
    i = 0;
    for func in funcs:
        res_str += gen_func(func, i)
        i += 1
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
    show_cpp_begin()
    print gen_funcs(funcs)
    show_cpp_end()
    print gen_socketpath(sock_path, namespace)
