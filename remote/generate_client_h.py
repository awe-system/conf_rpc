import load_xml as lx
from sys import argv
import gfuncs as gfs

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "


def help(arg):
    print "need xml path"


def show_def(namespace, filename):
    str = "#ifndef " + namespace.upper() + "_" + filename.upper() + "_H\n"
    str += "#define " + namespace.upper() + "_" + filename.upper() + "_H\n"
    print str


def show_include(namespace):
    str = "#include \"" + namespace + "_internal.h\"\n"
    print str


def show_end():
    print "#endif"


def show_main_head(namespace, classname, withping):
    print "namespace " + namespace + "\n{\n"
    print "class " + classname + "\n{\n"
    print "private:"

    if (withping):
        print ONE_TEB + "bool to_destroy;"
        print ONE_TEB + "std::thread * th;"
    print ONE_TEB + "lt_condition discon_cond;"
    print ONE_TEB + "std::mutex disconn_m;"
    print ONE_TEB + "bool is_now_connected;"
    print ONE_TEB + "bool is_user_discon;"
    print ONE_TEB + classname + "_client cli;\n"
    print "public:"
    print ONE_TEB + classname + "();"
    if (withping):
        print ONE_TEB + "virtual ~" + classname + "();"
        print ONE_TEB + "void run();"
    print ONE_TEB + "int connect(const std::string &ip);"
    print ONE_TEB + "void disconnect_async();"
    print ONE_TEB + "void disconnect();\n"


def show_sync_func(func):
    str = ONE_TEB + gfs.client_sync_head(func) + ";\n"
    print str


def show_async_func(func):
    str = ONE_TEB + gfs.client_async_head(func) + ";\n"
    print str


def show_async_callback(func):
    str = ONE_TEB + "virtual " + gfs.client_cb_head(func) + " = 0;\n"
    print str


def show_funcs(funcs):
    print "public:"
    for func in funcs:
        if (func["type"] == "sync"):
            show_sync_func(func)
        elif (func["subtype"] == "sync"):
            show_sync_func(func)
        else:
            show_async_func(func)


def show_callbacks(funcs):
    print "public:"
    print ONE_TEB + "void disconnected_internal();"
    print ONE_TEB + "virtual void disconnected();"
    for func in funcs:
        if (func["type"] == "async" and func["subtype"] != "sync"):
            show_async_callback(func)
    print ""


def show_main_end(funcs):
    print "};\n"
    print "}"


def show_main_class(namespace, classname, funcs, withping):
    show_main_head(namespace, classname, withping)
    show_callbacks(funcs)
    show_funcs(funcs)
    show_main_end(funcs)


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    classname = client["classname"]
    filename = client["filename"]
    withping = client["withping"]
    show_def(namespace, filename)
    show_include(filename)
    show_main_class(namespace, classname, funcs, withping)
    show_end()
