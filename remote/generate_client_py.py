import load_xml as lx
from sys import argv
import commands

BLANK = " "
ONE_TAB = "    "
TWO_TAB = "        "
THREE_TAB = "            "
FOUR_TAB = "                "


def show_base():
    head_py = commands.getoutput("cat src/client_python.py")
    print(head_py)


def pre_cli_type():
    return "client_function_callback_type_" + str(port)


def show_client_cb_type():
    pre_str = pre_cli_type()
    print("class " + pre_str + "(object):")
    i = 0
    for func in funcs:
        print(ONE_TAB + pre_str + "_" + func["func_name"] + " = " + str(i))
        i += 1
    print("\ncli_cb_type = " + pre_str + "()\n")

def pre_server_type():
    return "server_function_callback_type_" + str(port)

def show_server_cb_type():
    pre_str = "server_function_callback_type_" + str(port)
    print("class " + pre_str + "(object):")
    i = 0
    for func in funcs:
        print(ONE_TAB + pre_str + "_" + func["func_name"] + " = " + str(i))
        i += 1
    print("\nserv_cb_type = " + pre_str + "()\n")


def print_interval():
    print(
        "\n#################################################################################\n")


def show_port():
    print("port = " + str(port))


def cmd_param_list(func):
    str = ''
    for param in func["params"]:
        if (param["param_type"] != "out"):
            str += " ,"
            str += param["param_name"]
    if (len(str) > 0): return str[2:]
    return str


def cmd_param_list_after_param(func):
    str = ''
    for param in func["params"]:
        if(param["param_type"] != "out"):
            str += " ,"
            str += param["param_name"]
    return str


def cmd_header(func):
    str = ONE_TAB
    str += "def " + func["func_name"] + "(self"
    str += cmd_param_list_after_param(func)
    str += "):"
    return str


def gen_data_name_param_noself(func):
    return "gen_" + func["func_name"] + "_data(" + cmd_param_list(func) + ")"


def parse_data_name_param_noself(func):
    return "parse_" + func["func_name"] + "_data(recv_data)"


def show_class_main_func(func):
    print(cmd_header(func))
    print(TWO_TAB + "indata = self." + gen_data_name_param_noself(func))
    print(TWO_TAB + "recv_data = self.snd_rcv(indata)")
    print(TWO_TAB + "return self." + parse_data_name_param_noself(func))
    print("")


def gen_data_name_param(func):
    return "gen_" + func[
        "func_name"] + "_data(self" + cmd_param_list_after_param(func) + "):"


def show_size_of(param_name, param_type):
    str = "size_of_" + param_type + "("
    if (
            param_type == "string" or param_type == "char_p" or param_type == "data"):
        str += param_name
    str += ")"
    return str


def show_gen_param(param_name, param_type):
    print(TWO_TAB + "data_len += " + show_size_of(param_name, param_type))
    print(TWO_TAB + "data_buf += by_" + param_type + "(" + param_name + ")")
    print("")


def show_gen_data_func(func):
    print(ONE_TAB + "def " + gen_data_name_param(func))
    print(TWO_TAB + "data_buf = bytes()")
    print(TWO_TAB + "data_len = 0")
    if (func["type"] == "sync"):
        print(TWO_TAB + "_inter_sync_cond = 0 ")
    print(TWO_TAB + "internal_pri = 0  ")
    print(TWO_TAB + "func_type = serv_cb_type." + pre_server_type() + "_" + func[
        "func_name"])
    show_gen_param("func_type", "uint")
    for param in func["params"]:
        if (param["param_type"] != "out"):
            show_gen_param(param["param_name"], param["param_value"])
    if (func["type"] == "sync"):
        show_gen_param("_inter_sync_cond", "void_p")
    show_gen_param("internal_pri", "void_p")

    print(TWO_TAB + "snd_data = lt_data_t()")
    print(TWO_TAB + "snd_data.from_len_buf(data_len, data_buf)")
    print(TWO_TAB + "return snd_data")
    print("")


def parse_data_name_param(func):
    return "parse_" + func["func_name"] + "_data(self, recv_data):"


def show_parse_param(param_name, param_type):
    print(
        THREE_TAB + param_name + " = to_" + param_type + "(recv_data.buf[off:])")
    print(THREE_TAB + "off += " + show_size_of(param_name, param_type))
    print("")


def show_res_dic_item(param_name):
    print(FOUR_TAB + "\"" + param_name + "\": " + param_name + ",")


def show_parse_data(func):
    print(ONE_TAB + "def " + parse_data_name_param(func))
    print(TWO_TAB + "try:")
    print(THREE_TAB + "off = 0")

    show_parse_param("functype", "uint")
    for param in func["params"]:
        if (param["param_type"] != "in"):
            show_parse_param(param["param_name"], param["param_value"])
    show_parse_param("error_internal", "uint")
    if (func["type"] == "sync"):
        show_parse_param("internal_sync_cond_p", "void_p")
    show_parse_param("internal_pri", "void_p")

    print(THREE_TAB + "return 0, {")
    show_res_dic_item("functype")
    for param in func["params"]:
        if (param["param_type"] != "in"):
            show_res_dic_item(param["param_name"])
    show_res_dic_item("error_internal")
    print(THREE_TAB + "}")
    print(TWO_TAB + "except:")
    print(THREE_TAB + "return -1, {}")
    print("")


def cout_data_name_param(func):
    return "cout_" + func["func_name"] + "_output(self, res_dic):"


def show_cout_item(param_name, param_type):
    print(
        TWO_TAB + "res.update(to_screen_" + param_type + "(res_dic, \"" + param_name + "\"))")


def show_cout_output(func):
    print(ONE_TAB + "def " + cout_data_name_param(func))
    print(TWO_TAB + "res = {}")
    show_cout_item("functype", "uint")
    for param in func["params"]:
        if (param["param_type"] != "in"):
            show_cout_item(param["param_name"], param["param_value"])
    show_cout_item("error_internal", "uint")
    print(TWO_TAB + "print(json.dumps(res))")
    print("")


def show_class_func(func):
    show_cout_output(func)
    show_gen_data_func(func)
    show_parse_data(func)
    show_class_main_func(func)


def show_class():
    print("class " + classname + "(object):")
    classbase = commands.getoutput("cat src/py_client_class_base.py")
    print(classbase)
    for func in funcs:
        show_class_func(func)


def cmd_header(func):
    str = ONE_TAB
    str += "def " + func["func_name"] + "(self"
    str += cmd_param_list_after_param(func)
    str += "):"
    return str


def client_name():
    return classname + "_client"


def input_params(func):
    str = ''
    for param in func["params"]:
        if( param["param_type"] != "out"):
            str += ", "
            str += param["param_name"]
    if (len(str) > 0):
        return str[2:]
    return str


def getfunc(param):
    str = "from_arg_"
    if (param["param_value"] == "data"):
        str += param["param_type"]
    str += param["param_value"]
    return str

def get_from_arg_extra(param):
    str = ''
    if (param["param_value"] == "data"):
        str += ", \""
        str += param["param_name"]
        str += "\""
    return  str

def show_from_arg(param, i):
    print(
        ONE_TAB + param["param_name"] + " = " + getfunc(param) + "(arg[" + str(
            i) + "]"+get_from_arg_extra(param)+")")


def show_from_args(func):
    i = 0
    for param in func["params"]:
        if(param["param_type"] != "out" or param["param_value"] == "data"):
            show_from_arg(param, i)
            i += 1


def show_cmd(func):
    print("def " + func["func_name"] + "_cmd(" + client_name() + ", arg):")
    show_from_args(func)
    print(ONE_TAB + "err, outdata = " + client_name() + "." + func[
        "func_name"] + "(" + input_params(func) + ")")
    print(ONE_TAB + client_name() + ".cout_" + func[
        "func_name"] + "_output(outdata)")
    print("")


def show_cmds():
    for func in funcs:
        show_cmd(func)

def show_tab():
    print("cmd_tab = {")
    for func in funcs:
        print(ONE_TAB + "\""+func["func_name"]+"\": "+func["func_name"]+"_cmd,")
    print("}\n")

def get_func_help(func):
    str = func["func_name"] + " <in string ip> "
    for param in func["params"]:
        if (param["param_type"] != "out" or param["param_value"] == "data"):
            str += "<"+param["param_type"] + " " +param["param_value"] +" " +param["param_name"]+"> "
    return str


def show_help():
    print("def help():")
    print(ONE_TAB+"print(color_green)")
    print(ONE_TAB+'print("---------------- help ---------------")')
    for func in funcs:
        print(ONE_TAB+'print_colorfully()')
        print(ONE_TAB+'print("'+ get_func_help(func) +'")')
    print(ONE_TAB + 'print(color_reset)\n')

def show_main():
    head_py = commands.getoutput("cat src/client_main_head.py")
    print(head_py)
    print(TWO_TAB + client_name() + " = " + classname + "()")
    print(TWO_TAB + client_name() + ".connect(ip)")
    print(TWO_TAB + "cmd_tab[cmd]("+ client_name() + ", argv[3:])")
    end_py = commands.getoutput("cat src/client_main_end.py")
    print(TWO_TAB + client_name() + ".disconnect()")
    print(end_py)

def help(arg):
    print("need xml path")


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    classname = client["classname"]
    filename = client["filename"]
    withping = client["withping"]

    show_base()
    show_client_cb_type()
    show_server_cb_type()
    show_port()
    print_interval()
    show_class()
    show_cmds()
    show_tab()
    show_help()
    show_main()

