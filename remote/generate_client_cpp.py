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
    print ONE_TEB + "std::map<void * ,"+classname+" *> connected_list;"
    print "public:"


def show_handler_end():
    print "};\n"


def show_callback_head(func):
    print "\n" + ONE_TEB + gfs.client_inter_cb_head(func) + " override"
    print ONE_TEB + "{"


def show_callback_end():
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


def show_callback(func):
    show_callback_head(func)
    if (func["subtype"] == "sync"):
        show_sync_callback(func)
    else:
        show_async_callback(func)
    show_callback_end()


def show_callbacks(funcs):
    for func in funcs:
        if (func["type"] == "async"):
            show_callback(func)


def show_static_callbacks(classname):
    print ONE_TEB + "void addcli_to_event(void *sess,"+classname+" *cli)"
    print ONE_TEB + "{"
    print TWO_TEB + "std::unique_lock<std::mutex> lck(connected_list_m);"
    print TWO_TEB + "connected_list[sess] = cli;"
    print ONE_TEB + "}\n"
    print ONE_TEB + "void disconnected(lt_session *sess) override"
    print ONE_TEB + "{"
    print TWO_TEB + "std::unique_lock<std::mutex> lck(connected_list_m);"
    print TWO_TEB + classname+" *cli = connected_list[sess];"
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


def show_disconnected(classname):
    print "void " + classname + "::disconnected()"
    print "{"
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
        print THREE_TEB + "ping_internal();"
        print TWO_TEB + "}"
        print TWO_TEB + "else"
        print TWO_TEB + "{"
        print THREE_TEB + "break;"
        print TWO_TEB + "}"
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
    show_disconnected(classname)
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
