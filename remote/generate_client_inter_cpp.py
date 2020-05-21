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
    print "#include \"" + filename + ".h\""
    print "#include <awe_log.h>\n"
    print "namespace " + namespace
    print "{\n"


def show_port(port):
    print "#define SERVER_PORT    " + str(port) + "\n"

def show_client_common():
    print commands.getoutput("cat ./src/client_cpp_body")
    print classname + "_client::" + classname + "_client(" + classname + "_client_callback *_cb) : cb(_cb), sess(NULL)"
    print "{}"
    print ""
    print "int " + classname + "_client::connect(const std::string &ip)"
    print "{"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"connect before mutex ip [%s] cb [%p] sess [%p]\","
    print TWO_TEB + "ip.c_str(), cb, sess);"
    print ONE_TEB + "write_lock_t lck(m);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"connect after mutex ip [%s] cb [%p] sess [%p]\","
    print TWO_TEB + "ip.c_str(), cb, sess);"
    #print ONE_TEB + "if ( !sess )"
    #print ONE_TEB + "{"
    print ONE_TEB + "sess = cb->get_session(ip);"
    print ONE_TEB + "if ( !sess )"
    print TWO_TEB + "return -RPC_ERROR_TYPE_CONNECT_FAIL;"
    #print ONE_TEB + "}"
    print ONE_TEB + "try"
    print ONE_TEB + "{"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"before [%p]->connect(%s) cb [%p]\",sess, ip.c_str(), cb);"
    print TWO_TEB + "sess->connect(ip, SERVER_PORT);"
    print ONE_TEB + "__sync_add_and_fetch(&cb->connect_cnt, 1);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"after [%p]->connect(%s) cb [%p] \\nconnect_cnt [%lld] disconn_cnt [%lld]\", sess, ip.c_str(),cb->connect_cnt, cb->disconn_cnt);"
    print TWO_TEB + "_ip = ip;"
    print ONE_TEB + "} catch (...)"
    print ONE_TEB + "{"
    print TWO_TEB + "cb->put_session(sess);"
    print TWO_TEB + "return -RPC_ERROR_TYPE_CONNECT_FAIL;"
    print ONE_TEB + "}"
    print ONE_TEB + "return RPC_ERROR_TYPE_OK;"
    print  "}"
    print ""
    print "void " + classname + "_client::disconnect()"
    print "{"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"disconnect before mutex ip [%s] cb [%p] sess [%p]\",_ip.c_str(), cb, sess);"
    print ONE_TEB + "write_lock_t lck(m);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"disconnect after mutex ip [%s] cb [%p] sess [%p]\",_ip.c_str(), cb, sess);"
    print ONE_TEB + "if (!sess) return;"
    print ONE_TEB + "sess->disconnect();"
    print ONE_TEB + "__sync_add_and_fetch(&cb->disconn_cnt, 1);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate\", \"after [%p]->disconnect cb [%p] \\nconnect_cnt [%lld] disconn_cnt [%lld]\",sess, cb, cb->connect_cnt, cb->disconn_cnt);"
    print ONE_TEB + "cb->put_session(sess);"
    print ONE_TEB + "sess = NULL;"
    print "}"
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
    str = "int " + classname + "_client::" + func["func_name"] + "("
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


def show_notsession_check():
    print ONE_TEB + "read_lock_t lck(m);"
    print ONE_TEB + "if ( !sess )"
    print ONE_TEB + "{"
    print TWO_TEB + "__sync_add_and_fetch(&cb->nosession_cnt, 1);"
    print TWO_TEB + "AWE_MODULE_DEBUG(\"communicate snd\","
    print THREE_TEB + "\"!sess cb [%p] nosession_cnt [%lld] snd_ref_cnt [%lld]  sess [%p]\\n\""
    print THREE_TEB + "\"gendata_ref_cnt [%lld]  cb_cnt [%lld]\\n\""
    print THREE_TEB + "\"cb_error_cnt [%lld] cb_normal_cnt [%lld]\","
    print THREE_TEB + "cb, cb->nosession_cnt, cb->snd_ref_cnt, sess, cb->gendata_ref_cnt, cb->cb_cnt,"
    print THREE_TEB + "cb->cb_error_cnt, cb->cb_normal_cnt);"
    print TWO_TEB + "return -RPC_ERROR_TYPE_CONNECT_FAIL;"
    print ONE_TEB + "}"


def show_before_snd():
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate snd\","
    print TWO_TEB + "\"before snd sess [%p] cb [%p] nosession_cnt [%lld] snd_ref_cnt [%lld] \\n\""
    print TWO_TEB + "\"gendata_ref_cnt [%lld]  cb_cnt [%lld]\\n\""
    print TWO_TEB + "\"cb_error_cnt [%lld] cb_normal_cnt [%lld]\","
    print TWO_TEB + "sess, cb, cb->nosession_cnt, cb->snd_ref_cnt, cb->gendata_ref_cnt, cb->cb_cnt,"
    print TWO_TEB + "cb->cb_error_cnt, cb->cb_normal_cnt);"


def show_after_snd():
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate snd\","
    print TWO_TEB + "\"after snd sess [%p] cb [%p] nosession_cnt [%lld] snd_ref_cnt [%lld] \\n\""
    print TWO_TEB + "\"gendata_ref_cnt [%lld]  cb_cnt [%lld]\\n\""
    print TWO_TEB + "\"cb_error_cnt [%lld] cb_normal_cnt [%lld] errr[%d]\","
    print TWO_TEB + "sess, cb, cb->nosession_cnt, cb->snd_ref_cnt, cb->gendata_ref_cnt, cb->cb_cnt,"
    print TWO_TEB + "cb->cb_error_cnt, cb->cb_normal_cnt, err_report);"


def show_sync_client_func(func):
    show_notsession_check()
    print ONE_TEB + "int error_internal = 0;"
    print ONE_TEB + "lt_condition _internal_sync_cond;"
    print ONE_TEB + "__sync_add_and_fetch(&cb->snd_ref_cnt, 1);"
    show_before_snd()

    print ONE_TEB + "lt_data_t *data = new lt_data_t;"
    print ONE_TEB + func["func_name"] + "_gendata(" + put_sync_gendata_params_no_def(
        func) + " &_internal_sync_cond, internal_pri, data);"
    print ONE_TEB + "cb->snd(sess, data);"

    print ONE_TEB + "int err_internal = _internal_sync_cond.wait();"
    print ONE_TEB + "if ( err_internal < 0 )"
    print ONE_TEB + "{"
    print ONE_TEB + "    return err_internal;"
    print ONE_TEB + "}"
    print ONE_TEB + "const lt_data_t &res_data = _internal_sync_cond.get_data();"
    print ONE_TEB + "unsigned char *buf = res_data.get_buf();"
    show_sync_to_buf(func)
    print ONE_TEB + "error_internal = lt_data_translator::to_uint(buf);"
    print ONE_TEB + "int err_report = (err_internal | error_internal);"
    show_after_snd()
    print ONE_TEB + "return err_report;"


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
    show_notsession_check()
    print ONE_TEB + "__sync_add_and_fetch(&cb->snd_ref_cnt, 1);"
    show_before_snd()
    print ONE_TEB + "lt_data_t *data = new lt_data_t;"
    print ONE_TEB + func["func_name"] + "_gendata(" + put_async_gendata_params_no_def(
        func) + " internal_pri, data);"
    print ONE_TEB + "int err_report = cb->snd(sess, data);"
    show_after_snd()
    print ONE_TEB + "return err_report;"

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
    str = "int " + classname + "_client::"
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

    else:
        for param in func["params"]:
            if param["param_type"] != "out":
                print ONE_TEB + "lt_data_translator::by_" + param[
                    "param_value"] + "(" + param["param_name"] + ", buf);"
        print ONE_TEB + "lt_data_translator::by_void_p(internal_pri, buf);"


def show_gendata_log(prefix):
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate gendata\","
    print TWO_TEB + "\""+ prefix +" snd sess [%p] cb [%p] nosession_cnt [%lld] snd_ref_cnt [%lld] \\n\""
    print TWO_TEB + "\"gendata_ref_cnt [%lld]  cb_cnt [%lld]\""
    print TWO_TEB + "\"cb_error_cnt [%lld] cb_normal_cnt [%lld] func_type [%u]\","
    print TWO_TEB + "sess, cb, cb->nosession_cnt, cb->snd_ref_cnt, cb->gendata_ref_cnt, cb->cb_cnt,"
    print TWO_TEB + "cb->cb_error_cnt, cb->cb_normal_cnt, func_type);"


def show_sync_generate_data_func(func):
    show_sync_generate_data_func_def(func)
    print "{"
    print ONE_TEB + "unsigned int func_type = server_function_callback_type_" + \
          port + "_" + func["func_name"] + ";"
    print ONE_TEB + "__sync_add_and_fetch(&cb->gendata_ref_cnt, 1);"
    show_gendata_log("before")
    for param in func["params"]:
        if param["param_value"] == "data":
            p_name = param["param_name"]
            print ONE_TEB + "lt_data_t " + p_name + "(" + p_name + "_len, " + p_name + "_buf);"

    print ONE_TEB + get_gendate_data_len(func)
    print ONE_TEB + "data->realloc_buf();"
    print ONE_TEB + "unsigned char *buf = data->get_buf();"
    show_by_buf(func)
    show_gendata_log("after")
    print ONE_TEB + "return 0;"
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
    str = "int " + classname + "_client::"
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
          port + "_" + func["func_name"] + ";"
    print ONE_TEB + "__sync_add_and_fetch(&cb->gendata_ref_cnt, 1);"
    show_gendata_log("before")
    show_request_data(func)
    print ONE_TEB + get_async_gendate_data_len(func)
    print ONE_TEB + "data->realloc_buf();"
    print ONE_TEB + "unsigned char *buf = data->get_buf();"
    show_by_buf(func)
    show_gendata_log("after")
    print ONE_TEB + "return 0;"
    print "}\n"


def show_client_gendata():
    for func in funcs:
        if func["type"] == "sync":
            show_sync_generate_data_func(func)
        else:
            show_async_generate_data_func(func)


def show_client_callback_head():
    print classname + "_client_callback::" + classname + "_client_callback(int thread_num," \
                                                         " " + classname + "_callback_handler *cb_handler) :"
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


def show_byoutout_startlog(name):
    print THREE_TEB + "__sync_add_and_fetch(&cb_normal_cnt, 1);"
    print THREE_TEB + "__sync_add_and_fetch(&cb_cnt, 1);"
    print THREE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print THREE_TEB + ONE_TEB + "\"" + name + " normal start cb_normal_cnt [%lld] cb_cnt [%lld] this [%p] snd_ref_cnt [%lld] gendata_ref_cnt [%lld] \\n\","
    print THREE_TEB + ONE_TEB + "cb_normal_cnt, cb_cnt, this,snd_ref_cnt,gendata_ref_cnt);"


def show_byoutout_endlog(name):
    print THREE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print THREE_TEB + ONE_TEB + "\"" + name + " normal end cb_normal_cnt [%lld] cb_cnt [%lld] this [%p] snd_ref_cnt [%lld] gendata_ref_cnt [%lld]\\n\","
    print THREE_TEB + ONE_TEB + "cb_normal_cnt, cb_cnt, this,snd_ref_cnt,gendata_ref_cnt);"


def show_by_output_cases():
    for func in funcs:
        print TWO_TEB + "case client_function_callback_type_" + port + "_" + \
              func[
                  "func_name"] + ":"
        print TWO_TEB + "{"
        show_byoutout_startlog(func["func_name"])

        show_to_buf(func)
        if func["type"] == "sync":
            show_sync_notify(func)
        else:
            show_async_callback(func)
        show_byoutout_endlog(func["func_name"])
        print TWO_TEB + "}"
        print THREE_TEB + "break;"


def show_by_output():
    print "void " + classname + "_client_callback::handler_by_output(lt_data_t *received_data)"
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
            if param["param_type"] == "in":
                print THREE_TEB + "lt_data_translator::skip_" + param[
                    "param_value"] + "(buf);"


def show_byinput_starlog(name):
    print THREE_TEB + "__sync_add_and_fetch(&cb_error_cnt, 1);"
    print THREE_TEB + "__sync_add_and_fetch(&cb_cnt, 1);"
    print THREE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print THREE_TEB + ONE_TEB + "\"" + name + " Err start cb_normal_cnt [%lld] cb_cnt [%lld] err_internal [%d]\\n\""
    print THREE_TEB + ONE_TEB + "\"this [%p]\","
    print THREE_TEB + ONE_TEB + "cb_normal_cnt, cb_cnt, error_internal, this);"


def show_byinput_endlog(name):
    print THREE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print THREE_TEB + ONE_TEB + "\"" + name + " Err end cb_normal_cnt [%lld] cb_cnt [%lld] err_internal [%d]\\n\""
    print THREE_TEB + ONE_TEB + "\"this [%p]\","
    print THREE_TEB + ONE_TEB + "cb_normal_cnt, cb_cnt, error_internal, this);"


def show_by_input_cases():
    for func in funcs:
        print TWO_TEB + "case server_function_callback_type_" + port + "_" + \
              func[
                  "func_name"] + ":"
        print TWO_TEB + "{"
        show_byinput_starlog(func["func_name"])
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
                if param["param_type"] == "out":
                    if param["param_value"] == "data":
                        print THREE_TEB + param_declare_tab[
                            param["param_value"]] + BLANK + param[
                                  "param_name"] + "(1);"
                    else:
                        print THREE_TEB + param_declare_tab[
                            param["param_value"]] + BLANK + param[
                                  "param_name"] + ";"
                elif param["param_type"] == "inout":
                    print THREE_TEB + param_declare_tab[
                        param["param_value"]] + BLANK + param[
                              "param_name"] + " = lt_data_translator::to_" + \
                          param[
                              "param_value"] + "(buf);"

            print THREE_TEB + "void * internal_pri = lt_data_translator::to_void_p(buf);"
            show_async_callback(func)
            show_byinput_endlog(func["func_name"])
        print TWO_TEB + "}"
        print THREE_TEB + "break;"


def show_by_input():
    print "void " + classname + "_client_callback::handler_by_input(lt_data_t *sent_data, int error_internal)"
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
    print ""


def show_disconnected():
    print "void " + classname + "_client_callback::disconnected(lt_session *sess)"
    print "{"
    print ONE_TEB + "__sync_add_and_fetch(&disconnected_cnt, 1);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print TWO_TEB + "\"connect_cnt [%lld] disconn_cnt [%lld] disconnected [%lld] disconninthread_cnt [%lld] sess [%p] this [%p]\\n\","
    print TWO_TEB + "connect_cnt, disconn_cnt, disconnected_cnt, disconninthread_cnt, sess, this);"
    print ONE_TEB + "pool.submit_task(boost::bind("
    print TWO_TEB + "&" + classname + "_client_callback::disconnected_inthread, this,"
    print TWO_TEB + "sess));"
    print "}"
    print ""


def show_disconnected_inthread():
    print "void " + classname + "_client_callback::disconnected_inthread(lt_session *sess)"
    print "{"
    print ONE_TEB + "__sync_add_and_fetch(&disconninthread_cnt, 1);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print TWO_TEB + "\"connect_cnt [%lld] disconn_cnt [%lld] disconnected [%lld] disconninthread_cnt [%lld] sess [%p] this [%p]\\n\","
    print TWO_TEB + "connect_cnt, disconn_cnt, disconnected_cnt, disconninthread_cnt, sess, this);"
    print ONE_TEB + "lt_client_service::disconnected(sess);"
    print ONE_TEB + "cb_handler->disconnected(sess);"
    print ONE_TEB + "AWE_MODULE_DEBUG(\"communicate callback\","
    print TWO_TEB + "\"connect_cnt [%lld] disconn_cnt [%lld] disconnected [%lld] disconninthread_cnt [%lld] sess [%p] this [%p]\\n\","
    print TWO_TEB + "connect_cnt, disconn_cnt, disconnected_cnt, disconninthread_cnt, sess, this);"
    print "}"
    print ""


def show_client_callback():
    show_client_callback_head()
    show_by_output()
    show_by_input()
    show_disconnected()
    show_disconnected_inthread()


def show_end():
    print "}"


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    filename = client["filename"] + "_internal"
    classname = client["classname"]
    show_include(namespace, filename)
    show_port(port)
    show_client_common()
    show_client_funcs()
    show_client_gendata()
    show_client_callback()
    show_end()
