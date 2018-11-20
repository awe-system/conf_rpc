import load_xml as lx
from sys import argv
import generate_function_type_h as gf

BLANK = " "
ONE_TEB = "    "

type_tab = {
    "in": "IN",
    "out": "OUT",
    "inout": "INOUT"
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
    str = "#include <lt_server_service.h>\n"
    str += "#include <lt_data_translator.h>\n\n"
    str += "#ifndef IN\n#define IN\n#endif\n\n" \
           "#ifndef OUT\n#define OUT\n#endif\n\n" \
           "#ifndef INOUT\n#define INOUT\n#endif\n\n"
    str += "namespace " + namespace + "\n{\n"
    print str


def generate_param(param):
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


def server_handler_sync_params(func):
    str = ""
    for param in func["params"]:
        str += generate_param(param)
        str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def server_handler_async_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_param(param)
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_handler_func(func):
    str = ONE_TEB + "virtual int "
    str += func["func_name"] + "("
    if func["type"] == "sync":
        out_str = server_handler_sync_params(func)
    else:
        out_str = server_handler_async_params(func)

    if len(out_str) > 0:
        str += out_str

    if func["type"] == "sync":
        str += ") = 0;\n"
    else:
        str += ", void *server_context) = 0;\n"
    print str


def show_handler_funcs():
    for func in funcs:
        show_handler_func(func)


def show_server_handler():
    print "class server;\n"
    print "class server_handler"
    print "{"
    print "public:"
    show_handler_funcs()
    print "};\n"


def handler_done_output_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            str += generate_param(param)
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_handler_done_func(func):
    str = ONE_TEB + "virtual void "
    str += func["func_name"] + "_done" + "("
    out_str = handler_done_output_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "void *server_context, int error) = 0;\n"
    print str


def show_handler_done_funcs():
    for func in funcs:
        if func["type"] == "async":
            show_handler_done_func(func)


def show_server_handler_done():
    print "class server_handler_done"
    print "{"
    print "public:"
    show_handler_done_funcs()
    print "};\n"


def put_sync_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            str += gen_data_param_tab[param["param_value"]]
            str += BLANK
            str += param["param_name"]
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
    str += "int error, void *internal_sync_cond_p, lt_data_t *data);\n"
    print str


def put_async_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                if param["param_type"] != "out":
                    str += "const "
                str += "unsigned long "
                str += param["param_name"] + "_len"
                str += ", "
                str += "unsigned char *"
                str += param["param_name"] + "_buf"
            else:
                if param["param_type"] == "in":
                    str += "const "
                str += gen_data_param_tab[param["param_value"]]
                str += BLANK
                str += param["param_name"]
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_async_generate_data_func(func):
    str = ONE_TEB + "int "
    str += func["func_name"] + "_done_gendata" + "("
    out_str = put_async_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "void *server_context, int error, lt_data_t *data);\n"
    print str


def show_generate_data_funcs():
    for func in funcs:
        if func["type"] == "sync":
            show_sync_generate_data_func(func)
        else:
            show_async_generate_data_func(func)


def async_done_fun_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                if param["param_type"] != "out":
                    str += "const "
                str += "unsigned long &"
                str += param["param_name"] + "_len"
                str += ", "
                str += "unsigned char *"
                str += param["param_name"] + "_buf"
            else:
                if param["param_type"] == "in":
                    str += "const "
                str += param_tab[param["param_value"]]
                str += param["param_name"]
            str += ","
    if len(str) == 0:
        return str
    return str[:len(str) - 1]


def show_async_done_func(func):
    str = ONE_TEB + "void "
    str += func["func_name"] + "_done" + "("
    out_str = async_done_fun_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "void *server_context, int error);\n"
    print str


def show_async_done_funcs():
    for func in funcs:
        if func["type"] == "async":
            show_async_done_func(func)


def show_server_class():
    print "class server : public lt_server_callback, public server_handler_done"
    print "{"
    print "private:"
    print ONE_TEB + "lt_server_service service;\n"
    print ONE_TEB + "server_handler *handler;\n"
    print "public:"
    print ONE_TEB + "server(int thread_num, server_handler *_handler);\n"
    print ONE_TEB + "void do_func(lt_data_t *data, lt_session_serv *sess) override;\n"
    print "private:"
    show_generate_data_funcs()
    print "public:"
    show_async_done_funcs()
    print "};"


def show_class_end():
    print "}"
    print "#endif"


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server = lx.load_xml(argv[1])
    namespace = server["namespace"]
    filename = server["filename"]
    show_def(namespace, filename)
    gf.show_all(port, funcs)
    show_include(namespace)
    show_server_handler()
    show_server_handler_done()
    show_server_class()
    show_class_end()
