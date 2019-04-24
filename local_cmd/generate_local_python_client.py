import load_xml as lx
# import string
import json
from sys import argv

funcs = []
sock_path = ""


def help(arg):
    print "need xml path"


def gen_import():
    res_str = "#!/usr/bin/python\n"
    res_str += "import json\n"
    res_str += "import socket\n"
    res_str += "import os\n"
    res_str += "from sys import argv\n"
    res_str += "import sys\n"
    res_str += "import subprocess\n\n"
    return res_str


def gen_bool_tab():
    res_str = "bool_tab={\n"
    res_str += "\"0\":False,\n"
    res_str += "\"1\":True,\n"
    res_str += "}\n\n"
    return res_str


def gen_socket_path():
    res_str = "_socket_path = \""
    res_str += sock_path
    res_str += "\"\n\n"
    res_str += "def socket_path():return _socket_path\n\n"
    return res_str

def gen_send_cmd():
    res_str = "def recv_basic(the_socket):\n"
    res_str += "\ttotal_data=[]\n"
    res_str += "\twhile True:\n"
    res_str += "\t\tdata = the_socket.recv(512)\n"
    res_str += "\t\ttotal_data.append(data)\n"
    res_str += "\t\tif not data or len(data) < 512: break\n"
    res_str += "\treturn ''.join(total_data)\n"
    res_str += "\n\n"
    res_str += "def send_cmd_return_result(input):\n"
    res_str += "\ttry:\n"
    res_str += "\t\tclient = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)\n"
    res_str += "\t\tclient.connect(socket_path())\n"
    res_str += "\t\tclient.send(json.dumps(input)+'\\xff')\n"
    res_str += "\t\treturn 0,recv_basic(client)\n"
    res_str += "\texcept Exception,e:\n"
    res_str += "\t\tclient.close()\n"
    res_str += "\t\treturn 2,\"\\033[31m Err:socket wrong \\033[0m\"\n"
    res_str += "\n\n"
    return res_str


def check_arg_eixt(func):
    params_len = 0
    for param in func["params"]:
        if param["param_type"] == "out": continue
        params_len += 1
    if params_len == 0: return ""
    len_str = str(params_len)
    res_str = "\tif (len(arg)<" + len_str + "): return 1,\"\\033[31m Err:wrong type \\033[0m\"\n"
    return res_str


value_type_table = {
    "string": ["", ""],
    "long": ["long(", ")"],
    "ulong": ["long(", ")"],
    "int": ["int(", ")"],
    "uint": ["int(", ")"],
    "bool": ["bool_tab.get(", ",True)"],
    "list_string": ["json.loads(", ")"],
    "vec_string": ["json.loads(", ")"],
    "map_string": ["json.loads(", ")"],
}


def type_change_begin(value):
    return value_type_table[value][0]


def type_change_end(value):
    return value_type_table[value][1]


def value_set_param(param, i):
    if param["param_type"] == "out": return ""
    res_str = "\t"
    res_str += param["param_name"]
    res_str += "="
    res_str += type_change_begin(param["param_value"])
    res_str += "arg["
    res_str += str(i)
    res_str += "]"
    res_str += type_change_end(param["param_value"])
    res_str += "\n"
    return res_str


def value_set(func):
    res_str = ""
    i = 0
    for param in func["params"]:
        res_str += value_set_param(param, i)
        i += 1
    res_str += "\tglobal _socket_path\n"
    res_str += "\tif(len(arg) > " + str(i-1) +"): _socket_path = arg[" + str(i-1)+"]\n"
    return res_str


def gen_param(param):
    return param["param_name"]


def gen_params(params):
    res_str = ""
    for param in params:
        if param["param_type"] == "out": continue
        res_str += gen_param(param)
        res_str += ","
    res_str = res_str[0:len(res_str) - 1]
    return res_str


def gen_json_input(func):
    res_str = "\tinput={\n"
    res_str += "\t\"action\":\""
    res_str += func["func_name"]
    res_str += "\",\n"
    for param in func["params"]:
        if param["param_type"] == "out": continue
        res_str += "\t\"" + param["param_name"] + "\":";
        res_str += param["param_name"]
        res_str += ",\n"
    res_str += "}\n"
    return res_str


def gen_func(func):
    res_str = "def "
    res_str += func["func_name"]
    res_str += "("
    res_str += gen_params(func["params"])
    res_str += "):\n"
    res_str += gen_json_input(func)
    res_str += "\treturn send_cmd_return_result(input)\n"
    return res_str


def gen_funcs():
    res_str = ""
    for func in funcs:
        res_str += gen_func(func)
        res_str += "\n"
    return res_str


def gen_return_func(func):
    res_str = "\treturn "
    res_str += func["func_name"]
    res_str += "("
    res_str += gen_params(func["params"])
    res_str += ")"
    return res_str


def gen_cmd(func):
    res_str = "def "
    res_str += func["func_name"] + "_cmd"
    res_str += "(arg):\n"
    res_str += check_arg_eixt(func)
    res_str += value_set(func)
    res_str += gen_return_func(func)
    res_str += "\n"
    return res_str


def gen_cmds():
    res_str = ""
    for func in funcs:
        res_str += gen_cmd(func)
        res_str += "\n"
    return res_str


def gen_help():
    res_str = "def help(arg):\n"
    res_str += "\tprint \"-------------------------help-----------------------\"\n"
    for func in funcs:
        res_str += "\tprint \""
        res_str += func["func_name"]
        for param in func["params"]:
            if param["param_type"] == "out": continue
            res_str += " <"
            res_str += param["param_name"]
            res_str += ">("
            res_str += param["param_value"]
            if param["param_value"] == "bool": res_str += " 1/0"
            res_str += ")["
            res_str += param["param_type"]
            res_str += "] "
        res_str += " [socket_path]"
        res_str += "\"\n"
    res_str += "\n"
    return res_str


def gen_cmd_table():
    res_str = "cmd_table = {"
    for func in funcs:
        res_str += "\"" + func["func_name"] + "\":" + func["func_name"] + "_cmd,\n"
    res_str += "}\n"
    return res_str


def gen_main():
    res_str = "if __name__ == '__main__':\n"
    res_str += "\tif(len(argv) < 2):help(argv);exit(1)\n"
    res_str += "\terr, res = cmd_table.get(argv[1],help)(argv[2:])\n"
    res_str += "\tif (err):print >> sys.stderr,res;exit(err)\n"
    res_str += "\tprint json.dumps(json.loads(res),indent=2)\n"
    return res_str


if __name__ == '__main__':
    if (len(argv) < 2):
        help(argv)
        exit(1)
    funcs, sock, client, server = lx.load_xml(argv[1])
    sock_path = sock["name"]
    # print json.dumps(funcs)
    # print gen_cmd_table()
    # print gen_help()
    print gen_import()
    print gen_bool_tab()
    print gen_socket_path()
    print gen_send_cmd()
    print gen_funcs()
    print gen_cmds()
    print gen_cmd_table()
    print gen_help()
    print gen_main()
