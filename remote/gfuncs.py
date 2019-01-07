BLANK = " "

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

tranlate2buf_tab = {
    "string": "lt_data_translator::by_string",
    "char_p": "lt_data_translator::by_char_p",
    "uint": "lt_data_translator::by_uint",
    "ulong": "lt_data_translator::by_ulong",
    "bool": "lt_data_translator::by_bool",
    "void_p": "lt_data_translator::by_void_p",
    "data": "lt_data_translator::by_data"
}

frombuf_tab = {
    "string": "lt_data_translator::to_string",
    "char_p": "lt_data_translator::to_char_p",
    "uint": "lt_data_translator::to_uint",
    "ulong": "lt_data_translator::to_ulong",
    "bool": "lt_data_translator::to_bool",
    "void_p": "lt_data_translator::to_void_p",
    "data": "lt_data_translator::to_data"
}


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


def generate_func_value(param):
    str = ""
    if param["param_value"] == "data":
        str += param["param_name"] + "_len"
        str += ", "
        str += param["param_name"] + "_buf"
    else:
        str += param["param_name"]
    return str


def tanslate_params2buf(param, TAB_STR, BUF_STR):
    str = ""
    if (param["param_value"] == "data"):
        str += TAB_STR + "lt_data_t " + param["param_name"] + "(" + param[
            "param_name"] + "_len, " + param[
            "param_name"] + "_buf" +");"
        str += TAB_STR + tranlate2buf_tab[param["param_value"]] + "("
        str += param["param_name"]
        str += ", " + BUF_STR + ");\n"
    return str


def tanslate_buf2params(param, TAB_STR, BUF_STR):
    str = ""
    if (param["param_value"] == "data"):
        str += TAB_STR + "lt_data_t " + param["param_name"] + " = "
    else:
        str += TAB_STR + param["param_name"] + " = "
    str += frombuf_tab[param["param_value"]] + "(" + BUF_STR + ");\n"
    if (param["param_value"] == "data"):
        str += TAB_STR + param["param_name"] + "_len = " + param[
            "param_name"] + "._length;"
        str += TAB_STR + "memcpy(" + param["param_name"] + "_buf, " + param[
            "param_name"] + ".get_buf(), " + param["param_name"] + "_len);"
    return str


def generate_func_size(param):
    str = ""
    if param["param_value"] == "data":
        str += "sizeof(" + param["param_name"] + "_len)"
        str += " + " + param["param_name"] + "_len"
    else:
        str += "sizeof(" + param["param_name"] + ")"
    return str


def generate_all_param(params):
    str = ""
    for param in params:
        str += generate_func_param(param)
        str += ", "
    if (len(str) == 0): return ""
    return str[:len(str) - 2]


def generate_async_param(params):
    str = ""
    for param in params:
        if (param["param_type"] == "in" or param["param_type"] == "inout"):
            str += generate_func_param(param)
            str += ", "
    if (len(str) == 0): return ""
    return str[:len(str) - 2]


def generate_async_cb_param_doma_end(params):
    str = ""
    for param in params:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            str += generate_func_param(param)
            str += ", "
    return str


def client_sync_head(func):
    str = "int "
    str += func["func_name"] + "("
    str += generate_all_param(func["params"])
    str += ")"
    return str


def client_async_head(func):
    str = "int "
    str += func["func_name"] + "("
    str += generate_async_param(func["params"])
    str += ")"
    return str


def client_async_cb_values(func):
    str = ""
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            str += generate_func_value(param)
            str += ", "
    str += "error_internal"
    return str


def client_func_values(func):
    str = ""
    for param in func["params"]:
        if (param["param_type"] == "in" or param["param_type"] == "inout"):
            str += generate_func_value(param)
            str += ", "
    str += "internal_pri"
    return str


def client_sync_subasync_out_totalsize(func):
    str = ""
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            str += generate_func_size(param)
            str += " + "
    if (len(str) == 0): return str
    return str[:len(str) - 3]


def gen_cb_tanslate_params2buf(func, TAB_STR, BUF_STR):
    str = ""
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            str += tanslate_params2buf(param, TAB_STR, BUF_STR)
    return str


def gen_cb_tanslate_buf2params(func, TAB_STR, BUF_STR):
    str = ""
    for param in func["params"]:
        if (param["param_type"] == "out" or param["param_type"] == "inout"):
            str += tanslate_buf2params(param, TAB_STR, BUF_STR)
    return str


def client_cb_head(func):
    str = "void "
    str += func["func_name"] + "_callback("
    str += generate_async_cb_param_doma_end(func["params"])
    str += "int error_internal)"
    return str


def client_inter_cb_head(func):
    str = "void "
    str += func["func_name"] + "_callback("
    str += generate_async_cb_param_doma_end(func["params"])
    str += "INOUT void *&internal_pri, OUT int error_internal)"
    return str
