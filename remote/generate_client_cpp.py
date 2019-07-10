import load_xml as lx
from sys import argv
import gfuncs as gfs

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "


def help(arg):
    print "need xml path"


def show_include(namespace, filename):
    str = "#include <lt_data_translator.h>\n"
    str += "#include \"" + filename + ".h\"\n"
    str += "#include \"awe_conf/env.h\"\n"
    print str


def show_head(namespace, classname, project):
    print "namespace " + namespace + "\n{"
    print "env " + classname + "_threadnum(\"" + project + "\", \"" \
          + classname + "_threadnum\");"


def show_end():
    print "};\n"


def show_handler_head(classname):
    print "class " + classname + "_thread_handler : public " + classname + "_callback_handler"
    print "{"
    print "private:"
    print ONE_TEB + "std::mutex              connected_list_m;"
    print ONE_TEB + "std::map<void * ," + classname + " *> connected_list;"
    print ONE_TEB + "data_channel::thread_pool pool;"
    print "public:"
    print ONE_TEB + classname + "_thread_handler():pool(1){};\n"


def show_handler_end():
    print "};\n"


def show_callback_direct_head(func):
    print "\n" + ONE_TEB + gfs.client_inter_cb_direct_head(func) + ""
    print ONE_TEB + "{"


def gen_inthread_header(func):
    str = "void "
    str += func["func_name"] + "_callback_inthread("
    for param in func["params"]:
        if param["param_type"] != "in":
            if (param["param_value"] == "data"):
                str += "lt_data_t * " + param["param_name"]
            elif(param["param_value"] == "string"):
                str += "string * " + param["param_name"]
            elif(param["param_value"] == "char_p"):
                str += "char * " + param["param_name"]
            else:
                str += gfs.gen_data_param_tab[param["param_value"]] + " " + param["param_name"]
            str += ','
    str += "void *internal_pri,"
    str += "int error_internal)"
    return str

def show_callback_inthread_head(func):
    print "\n" + ONE_TEB + gen_inthread_header(func)
    print ONE_TEB + "{"


def show_callback_func_head(func):
    print "\n" + ONE_TEB + gfs.client_inter_cb_head(func) + " override"
    print ONE_TEB + "{"


def show_callback_func_end():
    print ONE_TEB + "}"


def show_async_callback(func):
    print TWO_TEB + classname + " *node = (" + classname + " *)internal_pri;"
    print TWO_TEB + "node->" + func[
        "func_name"] + "_callback(" + gfs.client_async_cb_values(func) + ");"


def show_sync_callback(func):
    if (gfs.in_param_num(func) > 0):
        print TWO_TEB + "lt_data_t res_data(" + gfs.client_sync_subasync_out_totalsize(
            func) + ");"
        print TWO_TEB + "unsigned char *res_buf = res_data.get_buf();"
    print gfs.gen_cb_tanslate_params2buf(func, TWO_TEB, "res_buf")
    print TWO_TEB + "lt_condition *_internal_sync_cond = (lt_condition *) internal_pri;"
    if (gfs.in_param_num(func) > 0):
        print TWO_TEB + "_internal_sync_cond->notify(res_data, error_internal);"
    else:
        print TWO_TEB + "_internal_sync_cond->notify();"


def gen_call_cb_direct(func):
    str = func["func_name"] + "_callback_direct("
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            str += gfs.generate_func_value(param)
            str += ", "
    str += "internal_pri, "
    str += "error_internal);"
    return str

def gen_post(func):
    str = "pool.submit_task(boost::bind(&" + classname + "_thread_handler::"
    str += func["func_name"] + "_callback_inthread, this,"
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            if ((param["param_value"] == "data") or
                    (param["param_value"] == "string") or
                    (param["param_value"] == "char_p")):
                str += "___new_" + param["param_name"]
            else:
                str += param["param_name"]
            str += ", "
    str += "internal_pri, "
    str += "error_internal));"
    return str

def show_cb_new_data(func):
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            if (param["param_value"] == "data"):
                print THREE_TEB + "lt_data_t * ___new_" + param[
                    "param_name"] + " = new lt_data_t(" + param[
                          "param_name"] + "_len);"
                print THREE_TEB + "assert("+param[
                    "param_name"] + "_len != 0);"
                print THREE_TEB + "memcpy(___new_" + param[
                    "param_name"] + "->get_buf(), " + param[
                          "param_name"] + "_buf, " + param[
                          "param_name"] + "_len);"
            elif (param["param_value"] == "string"):
                print THREE_TEB + "string * ___new_" + param[
                    "param_name"] + " = new string();"
                print THREE_TEB + "*___new_" + param[
                    "param_name"] + " = " + param[
                          "param_name"] + ";"
            elif (param["param_value"] == "char_p"):
                print THREE_TEB + "char * ___new_" + param[
                    "param_name"] + " = new char[strlen(" + param[
                          "param_name"] + ")];"
                print THREE_TEB + "memset(___new_" + param[
                    "param_name"] + ", 0 , strlen(" + param[
                          "param_name"] + ");"
                print THREE_TEB + "memcpy(___new_" + param[
                    "param_name"] + ", " + param[
                          "param_name"] + " , strlen(" + param[
                          "param_name"] + ");"


def show_callback_func(func):
    show_callback_func_head(func)
    print TWO_TEB + "if(!error_internal)"
    print TWO_TEB + "{"
    print THREE_TEB + gen_call_cb_direct(func)
    print TWO_TEB + "}"
    print TWO_TEB + "else"
    print TWO_TEB + "{"
    show_cb_new_data(func)
    print THREE_TEB + gen_post(func)
    print TWO_TEB + "}"
    show_callback_func_end()


def show_callback_direct(func):
    show_callback_direct_head(func)
    if (func["subtype"] == "sync"):
        show_sync_callback(func)
    else:
        show_async_callback(func)
    show_callback_func_end()

def gen_call_direct(func):
    str = func["func_name"] + "_callback_direct("
    for param in func["params"]:
        if param["param_type"] != "in":
            if (param["param_value"] == "data"):
                str += param["param_name"] + "->_length, "
                str += param["param_name"] + "->get_buf()"
            elif(param["param_value"] == "string"):
                str += "*" + param["param_name"]
            # elif(param["param_value"] == "char_p"):
            #     str += param["param_name"]
            else:
                str += param["param_name"]
            str += ', '

    str += "internal_pri, "
    str += "error_internal);\n"
    return str


def show_callback_inthread(func):
    show_callback_inthread_head(func)
    print TWO_TEB + gen_call_direct(func)
    for param in func["params"]:
        if param["param_type"] != "in":
            if ((param["param_value"] == "data") or
                    (param["param_value"] == "string") or
                    (param["param_value"] == "char_p")):
                print TWO_TEB + "delete " + param["param_name"] + ";"

    show_callback_func_end()


def show_callback(func):
    show_callback_func(func)
    show_callback_direct(func)
    show_callback_inthread(func)


def show_callbacks(funcs):
    for func in funcs:
        if (func["type"] == "async"):
            show_callback(func)


def show_static_callbacks(classname):
    print ONE_TEB + "void addcli_to_event(void *sess," + classname + " *cli)"
    print ONE_TEB + "{"
    print TWO_TEB + "std::unique_lock<std::mutex> lck(connected_list_m);"
    print TWO_TEB + "connected_list[sess] = cli;"
    print ONE_TEB + "}\n"
    print ONE_TEB + "void disconnected(lt_session *sess) override"
    print ONE_TEB + "{"
    print TWO_TEB + "std::unique_lock<std::mutex> lck(connected_list_m);"
    print TWO_TEB + classname + " *cli = connected_list[sess];"
    print TWO_TEB + "connected_list.erase((void *)sess);"
    print TWO_TEB + "cli->disconnected_internal();"
    print ONE_TEB + "}\n"


def show_handler(classname, funcs):
    show_handler_head(classname)
    show_callbacks(funcs)
    show_static_callbacks(classname)
    show_handler_end()


def show_static(classname):
    print "static " + classname + "_thread_handler handler;"
    print "static " + classname + "_client_callback cb(max(" + classname + "_threadnum.get_int(),1), &handler);"


def show_disconnected_internal(classname):
    print "void " + classname + "::disconnected_internal()"
    print "{"
    print ONE_TEB + "std::unique_lock<std::mutex> lck(disconn_m);"
    print ONE_TEB + "is_now_connected = false;"
    print ONE_TEB + "if ( is_user_discon )"
    print ONE_TEB + "{"
    print TWO_TEB + "cli.put_sess_ref();"
    print TWO_TEB + "lck.unlock();"
    print TWO_TEB + "discon_cond.notify();"
    print ONE_TEB + "}"
    print ONE_TEB + "else"
    print ONE_TEB + "{"
    print TWO_TEB + "lck.unlock();"
    print TWO_TEB + "disconnected();"
    print ONE_TEB + "}"
    print "}\n"

def show_disconnect(classname):
    print "void " + classname + "::disconnect()"
    print "{"
    print ONE_TEB + "std::unique_lock<std::mutex> lck(disconn_m);"
    print ONE_TEB + "if ( is_now_connected )"
    print ONE_TEB + "{"
    print TWO_TEB + "is_user_discon = true;"
    print TWO_TEB + "lck.unlock();"
    print TWO_TEB + "cli.disconnect();"
    print TWO_TEB + "discon_cond.wait();"
    print ONE_TEB + "}"
    print ONE_TEB + "else"
    print ONE_TEB + "{"
    print TWO_TEB + "lck.unlock();"
    print TWO_TEB + "cli.disconnect();"
    print ONE_TEB + "}"
    print "}\n"


def show_diconnect_async(classname):
    print "void " + classname + "::disconnect_async()"
    print "{"
    print ONE_TEB + "cli.disconnect();"
    print "}\n"


def show_connect(classname):
    print "int " + classname + "::connect(const std::string &ip)"
    print "{"
    print ONE_TEB + "is_user_discon = false;"
    print ONE_TEB + "int err = cli.connect(ip);"
    print ONE_TEB + "if ( !err )"
    print ONE_TEB + "{"
    print TWO_TEB + "cli.get_sess_ref();"
    print TWO_TEB + "handler.addcli_to_event(cli.get_sess(), this);"
    print TWO_TEB + "is_now_connected = true;"
    print ONE_TEB + "}"
    print ONE_TEB + "return err;"
    print "}\n"


def show_withping(classname, withping):
    if withping:
        print classname + "::~" + classname + " ()"
        print "{"
        print ONE_TEB + "to_destroy = true;"
        print ONE_TEB + "th->join();"
        print ONE_TEB + "delete th;"
        print "}\n"

        print "void " + classname + "::run()"
        print "{"
        print ONE_TEB + "while(!to_destroy)"
        print ONE_TEB + "{"
        print TWO_TEB + "std::unique_lock<std::mutex> lck(disconn_m);"
        print TWO_TEB + "if(is_now_connected)"
        print TWO_TEB + "{"
        print THREE_TEB + "int err = ping_internal();"
        print THREE_TEB + "if (err) is_now_connected = false;"
        print TWO_TEB + "}"
        print TWO_TEB + "lck.unlock();"
        print TWO_TEB + "sleep(min(DEFAULT_WAIT_SECONDS/3,3));"
        print ONE_TEB + "}"
        print "}\n"


def show_fix(classname, withping):
    if (withping):
        print "void *test_ping_func(" + classname + " *cli);"
    print classname + "::" + classname + "() : cli(&cb),is_user_discon(false),"
    if (withping):
        print TWO_TEB + "is_now_connected(false),to_destroy(false)"
        print "{"
        print ONE_TEB + "th = new thread(test_ping_func, this);"
        print "}\n"

        print "void *test_ping_func(" + classname + " *cli)"
        print "{"
        print ONE_TEB + "cli->run();"
        print ONE_TEB + "return nullptr;"
        print "}\n"
    else:
        print TWO_TEB + "is_now_connected(false){}\n"

    show_connect(classname)
    show_diconnect_async(classname)
    show_disconnect(classname)
    show_disconnected_internal(classname)
    show_withping(classname, withping)


def show_func_head(classname, func):
    str = "int " + classname + "::" + func["func_name"] + "("
    if (func["type"] == "sync" or func["subtype"] == "sync"):
        str += gfs.generate_all_param(func["params"])
    else:
        str += gfs.generate_async_param(func["params"])
    str += ")\n{"
    print str


def show_func_end():
    print "}\n"


def show_direct_func(func):
    print ONE_TEB + "void *internal_pri = (void *) this;"
    print ONE_TEB + "return cli." + func[
        "func_name"] + "(" + gfs.client_func_values(func) + ");"


def show_wait_func(func):
    print ONE_TEB + "lt_condition _internal_sync_cond;"
    print ONE_TEB + "void *internal_pri = (void *) &_internal_sync_cond;\n"
    print ONE_TEB + "int err_internal =  cli." + func[
        "func_name"] + "(" + gfs.client_func_values(func) + ");"
    print ONE_TEB + "if(err_internal) return err_internal;\n"
    print ONE_TEB + "int error_internal = _internal_sync_cond.wait();"
    print ONE_TEB + "if(error_internal) return error_internal;\n"

    if gfs.out_param_num(func) > 0:
        print ONE_TEB + "const lt_data_t &res_data = _internal_sync_cond.get_data();"
        print ONE_TEB + "unsigned char *buf = res_data.get_buf();\n"

    print gfs.gen_cb_tanslate_buf2params(func, ONE_TEB, "buf")
    print ONE_TEB + "return error_internal;\n"


def show_func_body(func):
    if (func["type"] == "async" and func["subtype"] == "sync"):
        show_wait_func(func)
    else:
        show_direct_func(func)


def show_dynamic(classname, funcs):
    for func in funcs:
        show_func_head(classname, func)
        show_func_body(func)
        show_func_end()


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    classname = client["classname"]
    filename = client["filename"]
    withping = client["withping"]
    show_include(namespace, filename)
    show_head(namespace, classname, project)
    show_handler(classname, funcs)
    show_static(classname)
    show_fix(classname, withping)
    show_dynamic(classname, funcs)
    show_end()
