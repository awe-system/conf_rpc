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
    str = "#include \"client2cachenode_internal.h\"\n"
    print str


def show_end():
    print "#endif"


def show_main_head(namespace):
    print "namespace " + namespace + "\n{\n"
    print "class " + namespace + "\n{\n"
    print "private:"
    print ONE_TEB + "client cli;\n"
    print "public:"
    print ONE_TEB + namespace + "();"
    print ONE_TEB + "int connect(const std::string &ip);"
    print ONE_TEB + "void disconnect();\n"


def show_sync_func(func):
    str = ONE_TEB + gfs.client_sync_head(func) + ";"
    print str


def show_async_func(func):
    str = ONE_TEB + gfs.client_async_head(func) + ";"
    print str


def show_async_callback(func):
    str = ONE_TEB + "virtual " + gfs.client_cb_head(func) + " = 0;"
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
    for func in funcs:
        if (func["type"] == "async" and func["subtype"] != "sync"):
            show_async_callback(func)
    print ""


def show_main_end(funcs):
    print "};\n"
    print "}"


def show_main_class(namespace, funcs):
    show_main_head(namespace)
    show_callbacks(funcs)
    show_funcs(funcs)
    show_main_end(funcs)


if __name__ == '__main__':
    if len(argv) < 2:
        help(argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    namespace = client["namespace"]
    filename = client["filename"]
    show_def(namespace, filename)
    show_include(namespace)
    show_main_class(namespace, funcs)
    show_end()
