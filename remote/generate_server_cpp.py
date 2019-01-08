import load_xml as lx
from sys import argv

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "

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


def show_async_class_context(func):
    print "class " + func["func_name"] + "_context : public lt_session_description"
    print "{"
    print "public:"
    print ONE_TEB +"void set_session_private(void *pri) override"
    print ONE_TEB + "{"
    print TWO_TEB + "sess->set_session_private(pri);"
    print ONE_TEB + "}\n"
    print ONE_TEB + "void *get_session_private() const override"
    print ONE_TEB + "{"
    print TWO_TEB + "return sess->get_session_private();"
    print ONE_TEB + "}\n"
    print ONE_TEB + "void *cli_pri;"
    print ONE_TEB + "lt_data_t *request_data;"
    print ONE_TEB + "lt_session_serv *sess;"
    for param in func["pt_params"]:
        if param["param_type"] == "param_passthrough":
            value_type = param_declare_tab[param["param_value"]]
            print ONE_TEB + value_type + param["param_name"] + ";"
    print "};\n"


def show_async_class_contexts():
    for func in funcs:
        if func["type"] == "async":
            show_async_class_context(func)


def show_constructor():
    print "server::server(int thread_num, server_handler *_handler) :"
    print "        service(thread_num, SERVER_PORT, this), handler(_handler)"
    print "{"
    print ONE_TEB + "service.start_accept();"
    print "}\n"


def show_to_buf(func):
    for param in func["params"]:
        if param["param_type"] != "out":
            print THREE_TEB + param_declare_tab[param["param_value"]] + BLANK + param["param_name"] + " = lt_data_translator::to_" + param["param_value"] + "(buf);"
    if func["type"] == "sync":
        print THREE_TEB + "void *internal_sync_cond_p = lt_data_translator::to_void_p(buf);"
        for param in func["params"]:
            if param["param_type"] == "out":
                print THREE_TEB + param_declare_tab[param["param_value"]] + BLANK + param["param_name"] + ";"
        print THREE_TEB + "void * internal_pri = lt_data_translator::to_void_p(buf);"
    else:
        print THREE_TEB + func["func_name"] + "_context *context = new " + func["func_name"] + "_context();"
        for param in func["pt_params"]:
            if param["param_type"] == "param_passthrough":
                print THREE_TEB + "context->" + param["param_name"] + " = lt_data_translator::to_" + param["param_value"] + "(buf);"
        print THREE_TEB + "context->sess = sess;"
        print THREE_TEB + "context->request_data = request_data;"
        print THREE_TEB + "context->cli_pri = lt_data_translator::to_void_p(buf);"


def generate_param(param):
    str = ""
    if param["param_value"] == "data":
        str += param["param_name"] + "._length"
        str += ", "
        str += param["param_name"] + ".get_buf()"
    else:
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


def gen_handler_params(func):
    out_str = ""
    if func["type"] == "sync":
        out_str = server_handler_sync_params(func)

    else:
        out_str = server_handler_async_params(func) + ", (lt_session_description  *) context"
    return out_str


def show_do_handler(func):
    str = THREE_TEB + "int error_internal = handler->" + func["func_name"] + "("
    str += gen_handler_params(func)
    str += ");"
    print str


def put_sync_snd_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                str += "&"
            str += param["param_name"]
            str += ", "
    return str


def show_sync_snd(func):
    str = THREE_TEB + "service.snd(sess, boost::bind(&server::" + func["func_name"] + "_gendata, this, "
    str += put_sync_snd_params(func)
    str += "error_internal, internal_sync_cond_p, internal_pri, _1));"
    print str


def show_switch():
    for func in funcs:
        print TWO_TEB + "case server_function_callback_type_" + func["func_name"] + ":"
        print TWO_TEB + "{"
        show_to_buf(func)
        show_do_handler(func)
        if func["type"] == "sync":
            show_sync_snd(func)
            print THREE_TEB + "delete request_data;"
        print TWO_TEB + "}"
        print THREE_TEB + "break;"


def show_do_func():
    print "void server::do_func(lt_data_t *received_data, lt_session_serv *sess)"
    print "{"
    print ONE_TEB + "lt_data_t *request_data = new lt_data_t();"
    print ONE_TEB + "*request_data = *received_data;"
    print ONE_TEB + "unsigned char *buf = request_data->get_buf();"
    print ONE_TEB + "unsigned int func_type = lt_data_translator::to_uint(buf);"
    print ONE_TEB + "switch ( func_type )"
    print ONE_TEB + "{"
    show_switch()
    print TWO_TEB + "default:"
    print THREE_TEB + "abort();"
    print ONE_TEB + "}"
    print "}"


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


def show_response_data(func):
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                p_name = param["param_name"]
                print ONE_TEB + "lt_data_t " + p_name + "(" + p_name + "_len, " + p_name + "_buf);"


def get_gendate_data_len(func):
    str = "data->_length = sizeof(func_type) + "
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                str += "sizeof(unsigned long) + "
                str += param["param_name"] + "->_length"
                str += " + "
            elif param["param_value"] == "string":
                str += param["param_name"] + ".length() + 1"
                str += " + "
            else:
                str += "sizeof("
                str += gen_data_param_tab[param["param_value"]]
                str += ")"
                str += " + "
    str += "sizeof(int) + sizeof(void *) + sizeof(void *);"
    return str


def show_by_buf(func):
    print ONE_TEB + "lt_data_translator::by_uint(func_type, res_buf);"

    if func["type"] == "sync":
        for param in func["params"]:
            if param["param_type"] != "in":
                if param["param_value"] == "data":
                    print ONE_TEB + "lt_data_translator::by_data(*" + param["param_name"] + ", res_buf);"
                else:
                    print ONE_TEB + "lt_data_translator::by_" + param["param_value"] + "(" + param["param_name"] + ", res_buf);"
        print ONE_TEB + "lt_data_translator::by_uint(error_internal, res_buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(internal_sync_cond_p, res_buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(internal_pri, res_buf);"
        print ONE_TEB + "return 0;"
    else:
        for param in func["params"]:
            if param["param_type"] != "in":
                print ONE_TEB + "lt_data_translator::by_" + param["param_value"] + "(" + param["param_name"] + ", res_buf);"
        for param in func["pt_params"]:
            print ONE_TEB + "lt_data_translator::by_" + param["param_value"] + "(context->" + param["param_name"] + ", res_buf);"
        print ONE_TEB + "lt_data_translator::by_uint(error_internal, res_buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(context->cli_pri, res_buf);"
        print ONE_TEB + "return 0;"


def show_sync_generate_data_func(func):
    str = "int server::"
    str += func["func_name"] + "_gendata" + "("
    out_str = put_sync_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "int error_internal, void *internal_sync_cond_p, void *internal_pri,lt_data_t *data)"
    print str
    print "{"
    print ONE_TEB + "unsigned int func_type = client_function_callback_type_" + func["func_name"] + ";"
    print ONE_TEB + get_gendate_data_len(func)
    print ONE_TEB + "data->realloc_buf();"
    print ONE_TEB + "unsigned char *res_buf = data->get_buf();"
    show_by_buf(func)
    print "}\n"


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


def get_async_gendate_data_len(func):
    str = "data->_length = sizeof(func_type) + "
    for param in func["params"]:
        if param["param_type"] != "in":
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
    for param in func["pt_params"]:
        str += "sizeof("
        str += gen_data_param_tab[param["param_value"]]
        str += ")"
        str += " + "
    str += "sizeof(void *) + sizeof(void *) + sizeof(error_internal);"
    return str


def show_async_generate_data_func(func):
    str = "int server::"
    str += func["func_name"] + "_done_gendata" + "("
    out_str = put_async_gendata_params(func)
    if len(out_str) > 0:
        str += out_str + ", "
    str += "lt_session_description *server_context, int error_internal, lt_data_t *data)"
    print str
    print "{"
    print ONE_TEB + func["func_name"] + "_context *context = (" + func["func_name"] + "_context *)" + "server_context;"
    print ONE_TEB + "unsigned int func_type = client_function_callback_type_" + func["func_name"] + ";"
    show_response_data(func)
    print ONE_TEB + get_async_gendate_data_len(func)
    print ONE_TEB + "data->realloc_buf();"
    print ONE_TEB + "unsigned char *res_buf = data->get_buf();"
    show_by_buf(func)
    print "}\n"


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


def put_call_async_gendata_params(func):
    str = ""
    for param in func["params"]:
        if param["param_type"] != "in":
            if param["param_value"] == "data":
                str += param["param_name"] + "_len"
                str += ", "
                str += param["param_name"] + "_buf"
            else:
                str += param["param_name"]
            str += ", "
    if len(str) == 0:
        return str
    return str[:len(str) - 2]


def show_done():
    for func in funcs:
        if func["type"] == "async":
            str = "void server::" + func["func_name"] + "_done("
            out_str = async_done_fun_params(func)
            if len(out_str) > 0:
                str += out_str + ", "
            str += "lt_session_description *server_context, int error_internal)\n"
            str += "{\n"
            str += ONE_TEB + func["func_name"] + "_context *context = (" + func["func_name"] + "_context *) server_context;\n"
            str += ONE_TEB + "lt_session_serv *sess = context->sess;\n"
            str += ONE_TEB + "int err_internal = service.snd(sess, boost::bind(&server::" + func["func_name"] + "_done_gendata, this, "
            out_str = put_call_async_gendata_params(func)
            if len(out_str) > 0:
                str += out_str + ", "
            str += "server_context, error_internal, _1));\n"
            str += ONE_TEB + "lt_data_t *request_data = context->request_data;\n"
            str += ONE_TEB + "delete request_data;\n"
            str += ONE_TEB + "delete context;\n"
            str += "}\n\n"
            print str


def show_end():
    print "}"


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server,project = lx.load_xml(argv[1])
    namespace = server["namespace"]
    filename = server["filename"]
    show_include(namespace, filename)
    show_port(port)
    show_async_class_contexts()
    show_constructor()
    show_do_func()
    show_generate_data_funcs()
    show_done()
    show_end()
