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

def generate_all_param(params):
    str = ""
    for param in params:
        str += generate_func_param(param)
        str += ", "
    if (len(str) == 0): return ""
    return str[:len(str)-2]

def generate_async_param(params):
    str = ""
    for param in params:
        if(param["param_type"] == "in" or param["param_type"] == "inout"):
            str += generate_func_param(param)
            str += ", "
    if (len(str) == 0): return ""
    return str[:len(str)-2]

def generate_async_cb_param(params):
    str = ""
    for param in params:
        if(param["param_type"] == "out" or param["param_type"] == "inout"):
            str += generate_func_param(param)
            str += ", "
    if (len(str) == 0): return ""
    return str[:len(str)-2]

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

def client_cb_head(func):
    str = "void "
    str += func["func_name"] + "_callback("
    str += generate_async_cb_param(func["params"])
    str += ", int error)"
    return str