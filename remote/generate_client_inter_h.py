import load_xml as lx
from sys import argv
import generate_function_type_h as gf

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "

type_tab = {
    "in": "IN",
    "out": "OUT",
    "inout": "INOUT",
    "param_passthrough": "INOUT"
}

param_tab = {
    "string": "std::string &",
    "char_p": "char * &",
    "uint": "unsigned int &",
    "ulong": "unsigned long &",
    "bool": "bool &",
    "void_p": "void *&",
}

gen_data_param_tab = {
    "string": "std::string",
    "char_p": "char *",
    "uint": "unsigned int",
    "ulong": "unsigned long",
    "bool": "bool",
    "void_p": "void *",
    "data": "lt_data_t *"
}


def help(arg):
    print "need xml path"


def show_def(namespace, filename):
    str = "#ifndef " + namespace.upper() + "_" + filename.upper() + "_H\n"
    str += "#define " + namespace.upper() + "_" + filename.upper() + "_H\n"
    print str


def show_include(namespace):
    str = "#include <lt_session.h>\n"
    str += "#include <lt_session_cli_safe.h>\n"
    str += "#include <lt_client_service.h>\n"
    str += "#include <lt_session_cli_set.h>\n"
    str += "#include <lt_data_translator.h>\n"
    str += "#include <lt_condition.h>\n\n"
    str += "#ifndef IN\n#define IN\n#endif\n\n" \
           "#ifndef OUT\n#define OUT\n#endif\n\n" \
           "#ifndef INOUT\n#define INOUT\n#endif\n\n"
    str += "namespace " + namespace + "\n{\n"
    print str


def generate_func_param(param):
    str = type_tab[param["param_type"]] + BLANK
    if param["param_value"] == "data":
        if param["param_type"] != "out":
            str += "const "
        str += "unsigned long &"
        str += param["param_name"] + "_len"
        str += ", "
        str += type_tab[param["param_type"]] + BLANK
        str += "unsigned char *"
        str += param["param_name"] + "_buf"
    else:
        if param["param_type"] == "in":
            str += "const "
        str += param_tab[param["param_value"]]
        str += param["param_name"]
    return str


def callback_handler_output_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            str += generate_func_param(param)
            str += ", "
    for param in func["pt_params"]:
        str += generate_func_param(param)
        str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_callback_handler():
    print "class callback_handler"
    print "{"
    print "public:"
    for func in funcs:
        if func["type"] == "async":
            str = ONE_TEB + "virtual void " + func["func_name"] + "_callback("
            out_str = callback_handler_output_params(func)
            if len(out_str) > 0:
                str += out_str + ", "
            str += "INOUT void *&internal_pri, int error_internal) = 0;\n"
            print str
    print "};\n"


def show_client_callback():
    print "class client_callback : public lt_client_service, public lt_session_cli_set"
    print "{"
    print "private:"
    print ONE_TEB + "callback_handler *cb_handler;"
    print ONE_TEB + "lt_thread_server server;\n"
    print "public:"
    print ONE_TEB + "client_callback(int thread_num, callback_handler *cb_handler);\n"
    print "private:"
    print ONE_TEB + "void handler_by_output(lt_data_t *received_data) override;\n"
    print ONE_TEB + "void handler_by_input(lt_data_t *sent_data, int error_internal) override;\n"
    print "};\n"


def show_client_head():
    print "class client"
    print "{"
    print "private:"
    print ONE_TEB + "client_callback *cb;"
    print ONE_TEB + "std::mutex m;"
    print ONE_TEB + "lt_session_cli_safe *sess;\n"
    print "public:"
    print ONE_TEB + "client(client_callback *_cb);\n"
    print ONE_TEB + "int connect(const std::string &ip);\n"
    print ONE_TEB + "void disconnect();\n"


def client_func_params(func):
    str = ""
    for param in func["params"]:
        if (func["type"] == "sync" or
                param["param_type"] == "in" or
                param["param_type"] == "inout"):
            str += generate_func_param(param)
            str += ", "
    str += "INOUT void *&internal_pri"
    return str


def show_client_func(func):
    str = ONE_TEB + "int " + func["func_name"] + "("
    str += client_func_params(func)

    if func["type"] == "sync":
        str += ");\n"
    else:
        out_str = ""
        for param in func["pt_params"]:
            out_str += param_tab[param["param_value"]]
            out_str += param["param_name"]
            out_str += ", "
        if len(out_str) > 0:
            str += ", " + out_str[:len(out_str) - 2]
        str += ");\n"
    print str


def show_client_funcs():
    for func in funcs:
        show_client_func(func)


def put_sync_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_func_param(param)
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_sync_generate_data_func(func):
    str = ONE_TEB + "int "
    str += func["func_name"] + "_gendata" + "("
    out_str = put_sync_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "lt_condition *_internal_sync_cond, INOUT void *&internal_pri, lt_data_t *data);\n"
    print str


def put_async_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_func_param(param)
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_async_generate_data_func(func):
    str = ONE_TEB + "int "
    str += func["func_name"] + "_gendata" + "("
    out_str = put_async_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "INOUT void *&internal_pri,"
    str += " lt_data_t *data);\n"
    print str


def show_client_gendata():
    print "private:"
    for func in funcs:
        if func["type"] == "sync":
            show_sync_generate_data_func(func)
        else:
            show_async_generate_data_func(func)


def show_client_tail():
    print "};"


def show_client():
    show_client_head()
    show_client_funcs()
    show_client_gendata()
    show_client_tail()


def show_end():
    print "}"
    print "#endif"


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    filename = client["filename"] + "_internal"
    show_def(namespace, filename)
    gf.show_all(port, funcs)
    show_include(namespace)
    show_callback_handler()
    show_client_callback()
    show_client()
    show_end()
