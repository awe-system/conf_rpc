import load_xml as lx
from sys import argv
import commands

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "

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

param_declare_tab = {
    "string": "std::string",
    "char_p": "char *",
    "uint": "unsigned int",
    "ulong": "unsigned long",
    "bool": "bool",
    "void_p": "void *",
    "data": "lt_data_t",
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


def show_include(namespace, filename):
    print "#include \"" + filename + ".h\"\n"
    print "namespace " + namespace
    print "{\n"


def show_port(port):
    print "#define SERVER_PORT    " + str(port) + "\n"


def show_client_common():
    print commands.getoutput("cat ./src/client_cpp_body")
    print ""


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


def client_func_params(func):
    str = ""
    for param in func["params"]:
        if (func["type"] == "sync" or
                param["param_type"] == "in" or
                param["param_type"] == "inout"):
            str += generate_param(param)
            str += ", "
    str += "INOUT void *&internal_pri"
    return str


def show_client_func_def(func):
    str = "int client::" + func["func_name"] + "("
    str += client_func_params(func)

    if func["type"] == "sync":
        str += ")"
    else:
        out_str = ""
        for param in func["pt_params"]:
            out_str += param_tab[param["param_value"]]
            out_str += param["param_name"]
            out_str += ", "
        if len(out_str) > 0:
            str += ", " + out_str[:len(out_str) - 2]
        str += ")"
    print str


def generate_gendata_param(param):
    str = ""
    if param["param_value"] == "data":
        str += param["param_name"] + "_len"
        str += ", "
        str += param["param_name"] + "_buf"
    else:
        str += param["param_name"]
    return str


def put_sync_gendata_params_no_def(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_gendata_param(param)
            str += ", "
    return str


def show_sync_to_buf(func):
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                print ONE_TEB + param_declare_tab[
                    param["param_value"]] + BLANK + param[
                          "param_name"] + " = lt_data_translator::to_" + param[
                          "param_value"] + "(buf);"
            else:
                print ONE_TEB + param[
                    "param_name"] + " = lt_data_translator::to_" + param[
                          "param_value"] + "(buf);"


def show_sync_client_func(func):
    print ONE_TEB + "int error_internal = 0;"
    print ONE_TEB + "lt_condition _internal_sync_cond;"
    print ONE_TEB + "cb->snd(sess, boost::bind(&client::" + func[
        "func_name"] + "_gendata, this, " + put_sync_gendata_params_no_def(
        func) + " &_internal_sync_cond, internal_pri, _1));"
    print ONE_TEB + "int err_internal = _internal_sync_cond.wait();"
    print ONE_TEB + "if ( err_internal < 0 )"
    print ONE_TEB + "{"
    print ONE_TEB + "    return err_internal;"
    print ONE_TEB + "}"
    print ONE_TEB + "const lt_data_t &res_data = _internal_sync_cond.get_data();"
    print ONE_TEB + "unsigned char *buf = res_data.get_buf();"
    show_sync_to_buf(func)
    print ONE_TEB + "error_internal = lt_data_translator::to_uint(buf);"
    print ONE_TEB + "return err_internal | error_internal;"


def put_async_gendata_params_no_def(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_gendata_param(param)
            str += ", "
    for param in func["pt_params"]:
        str += generate_gendata_param(param)
        str += ", "
    return str


def show_async_client_func(func):
    print ONE_TEB + "if ( !sess )"
    print TWO_TEB + "return -RPC_ERROR_TYPE_CONNECT_FAIL;"
    print ONE_TEB + "return cb->snd(sess, boost::bind(&client::" + func[
        "func_name"] + "_gendata, this, " + put_async_gendata_params_no_def(
        func) + " internal_pri, _1));"


def show_client_funcs():
    for func in funcs:
        show_client_func_def(func)
        print "{"
        if func["type"] == "sync":
            show_sync_client_func(func)
        else:
            show_async_client_func(func)
        print "}\n"


def put_sync_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_param(param)
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_sync_generate_data_func_def(func):
    str = "int client::"
    str += func["func_name"] + "_gendata" + "("
    out_str = put_sync_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "lt_condition *_internal_sync_cond,INOUT void *&internal_pri, lt_data_t *data)"
    print str


def get_gendate_data_len(func):
    str = "data->_length = sizeof(func_type) + "
    for param in func["params"]:
        if param["param_type"] != "out":
            if param["param_value"] == "data":
                str += "sizeof(unsigned long) + "
                str += param["param_name"] + "._length"
                str += " + "
            elif param["param_value"] == "string":
                str += param["param_name"] + ".length() + 1"
                str += " + "
            else:
                str += "sizeof("
                str += gen_data_param_tab[param["param_value"]]
                str += ")"
                str += " + "
    str += "sizeof(void *) + sizeof(void *);"
    return str


def show_by_buf(func):
    print ONE_TEB + "lt_data_translator::by_uint(func_type, buf);"

    if func["type"] == "sync":
        for param in func["params"]:
            if param["param_type"] != "out":
                if param["param_value"] == "data":
                    print ONE_TEB + "lt_data_translator::by_data(" + param[
                        "param_name"] + ", buf);"
                else:
                    print ONE_TEB + "lt_data_translator::by_" + param[
                        "param_value"] + "(" + param["param_name"] + ", buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(_internal_sync_cond, buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(internal_pri, buf);"
        print ONE_TEB + "return 0;"
    else:
        for param in func["params"]:
            if param["param_type"] != "out":
                print ONE_TEB + "lt_data_translator::by_" + param[
                    "param_value"] + "(" + param["param_name"] + ", buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(internal_pri, buf);"
        print ONE_TEB + "return 0;"


def show_sync_generate_data_func(func):
    show_sync_generate_data_func_def(func)
    print "{"
    print ONE_TEB + "unsigned int func_type = server_function_callback_type_"+ \
          port+ "_"  + func["func_name"] + ";"

    for param in func["params"]:
        if param["param_value"] == "data":
            p_name = param["param_name"]
            print ONE_TEB + "lt_data_t " + p_name + "(" + p_name + "_len, " + p_name + "_buf);"

    print ONE_TEB + get_gendate_data_len(func)
    print ONE_TEB + "data->realloc_buf();"
    print ONE_TEB + "unsigned char *buf = data->get_buf();"
    show_by_buf(func)
    print "}\n"


def put_async_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "out":
            str += generate_param(param)
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_async_generate_data_func_def(func):
    str = "int client::"
    str += func["func_name"] + "_gendata" + "("
    out_str = put_async_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "INOUT void *&internal_pri,"
    str += "lt_data_t *data)"
    print str


def show_request_data(func):
    for param in func["params"]:
        if param["param_value"] == "data" and param["param_type"] != "out":
            p_name = param["param_name"]
            print ONE_TEB + "lt_data_t " + p_name + "(" + p_name + "_len, " + p_name + "_buf);"


def get_async_gendate_data_len(func):
    str = "data->_length = sizeof(func_type) + "
    for param in func["params"]:
        if param["param_type"] != "out":
            if param["param_value"] == "data":
                str += "sizeof(unsigned long) + "
                str += param["param_name"] + "._length"
                str += " + "
            elif param["param_value"] == "string":
                str += param["param_name"] + ".length() + 1"
                str += " + "
            else:
                str += "sizeof("
                str += gen_data_param_tab[param["param_value"]]
                str += ")"
                str += " + "
    str += "sizeof(void *) + sizeof(void *);"
    return str


def show_async_generate_data_func(func):
    show_async_generate_data_func_def(func)
    print "{"
    print ONE_TEB + "unsigned int func_type = server_function_callback_type_" + \
          port+ "_" + func["func_name"] + ";"
    show_request_data(func)
    print ONE_TEB + get_async_gendate_data_len(func)
    print ONE_TEB + "data->realloc_buf();"
    print ONE_TEB + "unsigned char *buf = data->get_buf();"
    show_by_buf(func)
    print "}\n"


def show_client_gendata():
    for func in funcs:
        if func["type"] == "sync":
            show_sync_generate_data_func(func)
        else:
            show_async_generate_data_func(func)


def show_client_callback_head():
    print commands.getoutput("cat ./src/client_callback_head")


def show_to_buf(func):
    for param in func["params"]:
        if param["param_type"] != "in":
            print THREE_TEB + param_declare_tab[param["param_value"]] + BLANK + \
                  param["param_name"] + " = lt_data_translator::to_" + param[
                      "param_value"] + "(buf);"
    if func["type"] == "sync":
        print THREE_TEB + "unsigned int error_internal = lt_data_translator::to_uint(buf);"
        print THREE_TEB + "void *internal_sync_cond_p = lt_data_translator::to_void_p(buf);"
        print THREE_TEB + "void * internal_pri = lt_data_translator::to_void_p(buf);"
    else:
        for param in func["pt_params"]:
            print THREE_TEB + param_declare_tab[param["param_value"]] + BLANK + \
                  param["param_name"] + " = lt_data_translator::to_" + param[
                      "param_value"] + "(buf);"
        print THREE_TEB + "unsigned int error_internal = lt_data_translator::to_uint(buf);"
        print THREE_TEB + "void * internal_pri = lt_data_translator::to_void_p(buf);"


def gen_sync_res_data_len(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                str += "sizeof(unsigned long) + " + param[
                    "param_name"] + "._length "
            elif param["param_value"] == "string":
                str += param["param_name"] + ".length() + 1"
            else:
                str += "sizeof(" + param_declare_tab[param["param_value"]] + ")"
            str += " + "
    return str


def show_by_output_gen_res_buf(func):
    for param in func["params"]:
        if param["param_type"] != "in":
            print THREE_TEB + "lt_data_translator::by_" + param[
                "param_value"] + "(" + param["param_name"] + ", res_buf);"


def show_sync_notify(func):
    print THREE_TEB + "lt_data_t res_data(" + gen_sync_res_data_len(
        func) + "sizeof(error_internal));"
    print THREE_TEB + "unsigned char *res_buf = res_data.get_buf();"
    show_by_output_gen_res_buf(func)
    print THREE_TEB + "lt_data_translator::by_uint(error_internal, res_buf);"
    print THREE_TEB + "lt_condition *_internal_sync_cond = (lt_condition *) internal_sync_cond_p;"
    print THREE_TEB + "_internal_sync_cond->notify(res_data, error_internal);"


def generate_call_param(param):
    str = ""
    if param["param_value"] == "data":
        str += param["param_name"] + "._length"
        str += ", "
        str += param["param_name"] + ".get_buf()"
    else:
        str += param["param_name"]
    return str


def get_async_callback_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            str += generate_call_param(param)
            str += ", "
    for param in func["pt_params"]:
        str += generate_call_param(param)
        str += ", "
    return str


def show_async_callback(func):
    print THREE_TEB + "cb_handler->" + func[
        "func_name"] + "_callback(" + get_async_callback_params(
        func) + "internal_pri, error_internal);"


def show_by_output_cases():
    for func in funcs:
        print TWO_TEB + "case client_function_callback_type_" + port+ "_" + func[
            "func_name"] + ":"
        print TWO_TEB + "{"
        show_to_buf(func)
        if func["type"] == "sync":
            show_sync_notify(func)
        else:
            show_async_callback(func)
        print TWO_TEB + "}"
        print THREE_TEB + "break;"


def show_by_output():
    print "void client_callback::handler_by_output(lt_data_t *received_data)"
    print "{"
    print ONE_TEB + "unsigned char *buf = received_data->get_buf();"
    print ONE_TEB + "unsigned int func_type = lt_data_translator::to_uint(buf);"
    print ONE_TEB + "switch ( func_type )"
    print ONE_TEB + "{"
    show_by_output_cases()
    print TWO_TEB + "default:"
    print THREE_TEB + "abort();"
    print ONE_TEB + "}"
    print "}\n"


def show_skip_buf(func):
    if func["type"] == "sync":
        for param in func["params"]:
            if param["param_type"] != "out":
                print THREE_TEB + "lt_data_translator::skip_" + param[
                    "param_value"] + "(buf);"
    else:
        for param in func["params"]:
            if param["param_type"] != "out":
                print THREE_TEB + "lt_data_translator::skip_" + param[
                    "param_value"] + "(buf);"
    print THREE_TEB + "lt_data_translator::skip_void_p(buf);"


def show_by_input_cases():
    for func in funcs:
        print TWO_TEB + "case server_function_callback_type_" + port+ "_" + func[
            "func_name"] + ":"
        print TWO_TEB + "{"
        show_skip_buf(func)
        if func["type"] == "sync":
            print THREE_TEB + "void *internal_sync_cond_p = lt_data_translator::to_void_p(buf);"
            print THREE_TEB + "lt_data_t res_data;"
            print THREE_TEB + "lt_condition *_internal_sync_cond = (lt_condition *) internal_sync_cond_p;"
            print THREE_TEB + "void * internal_pri;"
            print THREE_TEB + "_internal_sync_cond->notify(res_data, error_internal);"
        else:
            for param in func["pt_params"]:
                print THREE_TEB + param_declare_tab[
                    param["param_value"]] + BLANK + param[
                          "param_name"] + " = lt_data_translator::to_" + param[
                          "param_value"] + "(buf);"
            for param in func["params"]:
                if param["param_type"] != "in":
                    print THREE_TEB + param_declare_tab[
                        param["param_value"]] + BLANK + param[
                              "param_name"] + ";"
            print THREE_TEB + "void * internal_pri;"
            show_async_callback(func)
        print TWO_TEB + "}"
        print THREE_TEB + "break;"


def show_by_input():
    print "void client_callback::handler_by_input(lt_data_t *sent_data, int error_internal)"
    print "{"
    print ONE_TEB + "unsigned char *buf = sent_data->get_buf();"
    print ONE_TEB + "unsigned int func_type = lt_data_translator::to_uint(buf);"
    print ONE_TEB + "switch ( func_type )"
    print ONE_TEB + "{"
    show_by_input_cases()
    print TWO_TEB + "default:"
    print THREE_TEB + "abort();"
    print ONE_TEB + "}"
    print "}"


def show_client_callback():
    show_client_callback_head()
    show_by_output()
    show_by_input()


def show_end():
    print "}"


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    filename = client["filename"] + "_internal"
    show_include(namespace, filename)
    show_port(port)
    show_client_common()
    show_client_funcs()
    show_client_gendata()
    show_client_callback()
    show_end()
