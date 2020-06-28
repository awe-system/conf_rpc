#!/usr/bin/python2.7
# coding:utf-8
import load_xml as lx
import sys
import copy
import gfuncs as gfs
from generate_client_py import BLANK, ONE_TAB, TWO_TAB, THREE_TAB, FOUR_TAB

FUNC_NAME_SET_IP = "set_ip_address"
FUNC_NAME_CONNECT = "connect"

class import_declaration(object):
    module_list = []

    # mods: str
    def add_module(self, *mods):
        for mod in mods:
            import_declaration.module_list.append(mod)

    def get_import_decl_str(self):
        str = "import (\n"
        for mod in import_declaration.module_list:
            str += ONE_TAB + "\"" + mod + "\"\n"
        str += ")\n"
        return str


class const_var_decl(object):
    def __init__(self):
        self.const_var_list = []

    def add_const_var(self, *vars):
        for var in vars:
            self.const_var_list.append(var)

    def get_const_var_decl_str(self):
        str = "const (\n"
        for var in self.const_var_list:
            str += ONE_TAB + var.name
            if var.default_value == None:
                str +=  " = iota\n"
            else:
                str += " = " + var.default_value + "\n"

        str += ")\n"
        return str


class var_name(object):
    name = ""
    type = ""

    def __init__(self, name, type, default_value = None):
        self.name = name
        self.type = type
        self.default_value = default_value

    def show_info(self):
        print("parameter name:" + self.name)
        print("parameter type:" + self.type)


class parameter(var_name):
    inout = ""

    def __init__(self, param):
        name, type, inout = get_xml_params_info(param)
        go_type = parameter.type_transform(type)
        var_name.__init__(self, name, go_type)
        self.inout = inout

    def show_info(self):
        print("parameter name:" + self.name)
        print("parameter type:" + self.type)
        print("parameter inout:" + self.inout)
        print("")

    @staticmethod
    def type_transform(xml_type):
        para_type = ""
        tbl = {
            "string":"string",
            "char_p":"string",
            #"char_p": ValueError("No support for type 'char_p', Please use 'string' instead."),
            "ulong" :"uint64",
            "uint"  :"uint32",
            #"bool"  :"int8",
            "bool"  : ValueError("No support for type 'bool'. Please use 'uint' instead."),
            "data"  :"[]byte",
            "void_p":"uint64"
        }

        try:
            para_type = tbl[xml_type]
            if isinstance(para_type, Exception):
                raise para_type
        except KeyError:
            print("Type:" + xml_type + " is not supported in Go Client Rpc!")

        return para_type


# 描述参数列表 结构体和函数共用
class params_obj(object):

    def __init__(self, name):
        self.name = name
        self.params = []

    # 同时支持下标和 键值 访问
    def __getitem__(self, index):
        if type(index) == int:
            return self.params[index]
        else:
            for para in self.params:
                if isinstance(para, var_name) and para.name == index:
                    return para
                elif isinstance(para, function_obj) \
                    and type(index) == str \
                    and para.func_name.lower() == index.lower():
                    return para

    def __len__(self):
        return len(self.params)

    def __copy__(self):
        that = type(self)(self.name)
        that.params = copy.copy(self.params)
        return that

    def add_param(self, para):
        self.params.append(para)

    def append(self, para):
        self.add_param(para)

    def get_params_list_str(self, prefix=None, capitalize=False, withblank=False, start=0):
        str = "" if not withblank else "("
        has_prefix = False
        if prefix is not None:
            has_prefix = True
        for index, p in enumerate(self.params):
            if index < start:
                continue
            name_str = p.name.capitalize() if capitalize else p.name
            if has_prefix:
                str += prefix + "." + name_str
            else:
                str += name_str
            if index < len(self.params) - 1:
                str += ", "

        str += "" if not withblank else ")"

        return str


class struct_obj(params_obj):

    def __init__(self, name):
        super(struct_obj, self).__init__(name)

    def get_declaration_str(self, capitalize = True):
        str = "type " + self.name + " struct" + "{ \n"
        for var in self.params:
            varname = var.name.capitalize() if capitalize else var.name
            str += ONE_TAB + varname + " " + var.type + "\n"
        str += "}\n"
        return str


class interface_obj(params_obj):

    def __init__(self, name):
        super(interface_obj, self).__init__(name)

    def get_declaration_str(self):
        str = "type " + self.name + " interface {\n"
        for func in self.params:
            str += ONE_TAB + func.get_func_signature() + "\n"
        str += "}\n"
        return str


class interface_implementer(object):

    # interface: interface_obj
    def __init__(self, interface, impl_struct, impl_name):
        self.interface = interface
        self.impl_varname = var_name(impl_name, " *" + impl_struct.name)
        self.impl_struct = impl_struct

    def get_func_signature(self, func):
        str = "func " + "(" + self.impl_varname.name + " " + self.impl_varname.type + ")"
        str += func.name

    def get_func(self, func_name):
        fn = None
        for func in self.interface.params:
            if isinstance(func, function_obj) and func.func_name.lower() == func_name:
                fn = func
        return fn

class function_obj(object):
    def __init__(self, name):
        self.params = params_obj("params")
        self.return_values = params_obj("return value")
        self.func_name = name

    def add_param(self, *paras):
        for para in paras:
            self.params.append(para)

    def add_return_value(self, *paras):
        for para in paras:
            self.return_values.append(para)

    def show_info(self):
        print("function name:" + self.func_name)
        self._show_params_info("params", self.params)
        self._show_params_info("return params", self.return_values)

    # 返回描述该函数对象的var_name，
    def func_type_var_name(self, name):
        return var_name(name, self.func_name)

    # 函数签名 声明语句 func_name(arg1 type1, ...) 定义时加前缀func
    def get_func_signature(self):
        str = self.func_name
        str += self._get_func_decl_para_list_str()
        return str

    # 该函数实现某个接口函数时，定义时多一个(impl *impl_type) func_name(args...) 定义时加"func "
    def get_func_signature_with_impl(self, impl_var):
        str = "(" + impl_var.name + " " + impl_var.type + ") "
        str += self.get_func_signature()
        return str

    # 只声明函数的类型声明语句 (typedef)
    def get_func_typedef_str(self):
        str = "type " + self.func_name + " func" + self._get_func_decl_para_list_str()
        return str

    # 函数定义或声明时的输入和返回参数列表字符串:(in_val in_type,...) [(ret_val ret_type,...)]
    def _get_func_decl_para_list_str(self):
        str = "("
        str += self._get_para_list_str(self.params.params)
        str += ")"
        if len(self.return_values) > 0:
            str += " (" + self._get_para_list_str(self.return_values) + ")"
        return str

    def _get_para_list_str(self, params, with_typename = True):
        str = ""
        for index, para in enumerate(params):
            str += para.name
            if with_typename:
                str += " " + para.type
            if index < len(self.params) - 1:
                str += ", "
        return str

    def _show_params_info(self, params_name, params_list):
        print("function " + self.func_name + " param list:" + params_name + ", len:" + str(len(params_list)))
        for para in params_list:
            para.show_info()
        print("")


class xml_define_function(function_obj):
    type = ""
    sub_type = ""
    is_async = False
    is_ping_internal = False

    def __init__(self, func):
        name, type, sub_type, pt_params, params = get_xml_func_info(func)
        super(xml_define_function, self).__init__(name.capitalize())

        self.type = type
        self.sub_type = sub_type
        self.is_async = xml_define_function._is_async(sub_type)

        self.param_in = params_obj("param_in")
        self.param_out = params_obj("param_out")
        self.pt_params = params_obj("obj")

        if str(name).lower() == "ping_internal":
            self.is_ping_internal = True
        else:
            self.is_ping_internal = False

        for para in params:
            pa = parameter(para)
            if pa.inout == "out":
                self.param_out.append(pa)
            elif pa.inout == "in":
                self.param_in.append(pa)
            elif pa.inout == "inout":
                self.param_in.append(pa)
                self.param_out.append(pa)

        for para in pt_params:
            pa = parameter(para)
            self.pt_params.append(pa)

        self._init_subsidiary_data()

        if self.is_async:
            self._init_async_data()

        self._init_func_param()

    def _init_func_param(self):
        self.params = copy.copy(self.param_in)
        if self.is_async:
            self.params.append(self.callback_api_functype.func_type_var_name("callback"))
        else:
            self.return_values = copy.copy(self.param_out)

    def _init_subsidiary_data(self):
        self.request_struct = struct_obj(self.func_name.lower() + "_request")
        var_functype = var_name("functype", "uint32")
        self.request_struct.add_param(var_functype)
        for para in self.param_in:
            self.request_struct.add_param(para)

        self.response_struct = struct_obj(self.func_name.lower() + "_response")
        self.response_struct.add_param(var_functype)
        for para in self.param_out:
            self.response_struct.add_param(para)

    def _init_async_data(self):
        self.callback_api_functype = function_obj("Callback_func_" + self.func_name.lower())
        for para in self.param_out.params:
            self.callback_api_functype.add_param(para)
        self.callback_api_functype.add_param(var_name("err", "error"))

        self.param_struct = struct_obj(self.func_name.lower() + "_param")
        self.param_struct.add_param(var_name("request", "*" + self.request_struct.name))
        self.param_struct.add_param(self.callback_api_functype.func_type_var_name("func_callback"))

        self.func_callback = function_obj(self.func_name.lower() + "_call_back")
        self.func_callback.add_param(var_name("param", "interface{}"))
        self.func_callback.add_param(var_name("reply", "interface{}"))
        self.func_callback.add_param(var_name("err", "error"))

    # 该函数的functype常量枚举定义
    def get_const_func_type_enum_str(self, port):
        # NOTE: 待优化
        str = "client_function_callback_type_" + port + "_" + self.func_name.lower()
        self.const_call_back_func_enum_str = str
        return str

    def get_async_callback_func_signature(self):
        str = self.func_callback.get_func_signature()
        return str

    def get_self_func_content_str(self, implementer):
        if self.is_ping_internal:
            raise RuntimeError(" Implement for ping internal function is not supported")

        package_name = manager.config.package_name

        str = "func "
        str += self.get_func_signature_with_impl(implementer)
        str += " {\n"

        str += ONE_TAB + "req := " + self.request_struct.name + " {\n"
        str += TWO_TAB + self.const_call_back_func_enum_str + "," + "\n"
        str += TWO_TAB + self.request_struct.get_params_list_str(None, False, False, 1) + "}\n"

        str += ONE_TAB + "var reply " + self.response_struct.name + "\n"
        str += ONE_TAB + "reply." + self.response_struct.params[0].name.capitalize()\
               + " = " + self.const_call_back_func_enum_str + "\n"

        if not self.is_async:
            str += ONE_TAB + implementer.name + ".client.Call(\"" + package_name + "\""
            str += ONE_TAB + ", req, &reply)\n"
            str += ONE_TAB + "return " + self.return_values.get_params_list_str("reply", True)
        else:
            str += ONE_TAB + "param := " + self.param_struct.name + "{&req, callback}\n"
            str += ONE_TAB + implementer.name + ".client.Go(" + "\"" + self.func_name + "\","\
                             " req, &reply, nil, &param, " + self.func_callback.func_name + ")\n"

        str += "}\n"

        return str

    def get_call_back_func_content_str(self):
        str = "func " + self.func_callback.get_func_signature() + "{\n"

        str += ONE_TAB + "if err != nil {\n"
        str += TWO_TAB + "fmt.Println(err.Error())\n"
        str += TWO_TAB + "return\n"
        str += ONE_TAB + "}\n"
        str += ONE_TAB + "pa, ok_param := param.(*" + self.param_struct.name + ")\n"
        str += ONE_TAB + "res, ok_reply := reply.(*" + self.response_struct.name + ")\n"
        str += ONE_TAB + "if ok_param && ok_reply {\n"
        str += TWO_TAB + "func_ptr := pa.Func_callback\n"
        str += TWO_TAB + "if func_ptr != nil {\n"
        str += THREE_TAB + "func_ptr(" + self.param_out.get_params_list_str("res", True) + ", err)\n"
        str += TWO_TAB + "}\n"
        str += ONE_TAB + "}\n"
        str += "}\n"
        return str

    def get_func_str(self):
        str = ""

    def show_info(self):
        print("function name:" + self.func_name)
        print("function type:" + self.type)
        print("function sub_type:" + self.sub_type)
        self._show_params_info("param_in", self.param_in)
        self._show_params_info("param_out", self.param_out)
        self._show_params_info("pt_params", self.pt_params)

    @staticmethod
    def _is_async(str):
        return str == "async"


class global_config(object):
    def __init__(self):
        pass

    def init(self, port, namespace, filename, withping):
        self.port = port
        self.package_name = namespace
        self.filename = filename
        self.withping = withping

    def show_info(self):
        print("config port:" + self.port)
        print("config package_name:" + self.package_name)
        print("config filename:" + self.filename)
        print("config withping:" + str(self.withping))


class global_manager(object):
    config = global_config()
    xml_funcs = {}
    primary_funcs = {}
    default_ipaddr = var_name("default_ip_address", "string")
    port_content = var_name("", "string")
    rpc_client = struct_obj("rpc_client".capitalize())
    global_interface = interface_obj("interface")
    interface_impl = interface_implementer(global_interface, rpc_client, "cli")
    import_decl = import_declaration()

    def __init__(self):
        self._init_primary_funcs()
        self._init_rpc_client()
        self._init_import()

    def init_config(self, port, namespace, filename, withping):
        self.config.port = port
        self.config.package_name = namespace
        self.config.filename = filename
        self.config.withping = withping
        self._init_interface(filename + "_interface")
        self.port_content.name = namespace + "_port"
        self.port_content.default_value = "\"" + port + "\""

    def init_xml_funcs(self, funcs):
        for func in funcs:
            fn = xml_define_function(func)
            if fn.is_ping_internal:
                self.func_ping_internal = fn
            self.xml_funcs[fn.func_name.lower()] = fn

    def _init_import(self):
        self.import_decl.add_module("fmt", "os/exec", "trace_rpc")

    def _init_primary_funcs(self):
        func_connect = function_obj(FUNC_NAME_CONNECT.capitalize())
        func_set_ip = function_obj(FUNC_NAME_SET_IP.capitalize())
        func_set_ip.add_param(var_name("ip", "string"))
        self.primary_funcs[FUNC_NAME_CONNECT] = func_connect
        self.primary_funcs[FUNC_NAME_SET_IP] = func_set_ip

    def _init_rpc_client(self):
        global_manager.rpc_client.add_param(var_name("client", "* trace_rpc.Client"))
        global_manager.rpc_client.add_param(var_name("ipaddr", "string"))

    def _init_interface(self, name):
        self.global_interface.name = name
        for func in self.primary_funcs.values() + self.xml_funcs.values():
            if hasattr(func, "is_ping_internal") and func.is_ping_internal == True:
                continue
            global_manager.global_interface.append(func)

    def show_info(self):
        self.config.show_info()
        print("XML defined functions:")
        for key, func in self.xml_funcs.items():
            func.show_info()
        print("Primary functions:")
        for key, func in self.primary_funcs.items():
            func.show_info()


class code_writer(object):
    def init_manager(self, manager):
        if isinstance(manager, global_manager) == False:
            raise TypeError("Manager in code_writer type error")
            exit(-1)
        self.manager = manager

    def write_package_header(self, package_name):
        str = "package " + package_name + "\n"
        print(str)

    def write_import(self):
        str = manager.import_decl.get_import_decl_str()
        print(str)

    def write_port(self, port, package_name):
        const_decl = const_var_decl()
        const_decl.add_const_var(manager.port_content)
        str = const_decl.get_const_var_decl_str()
        print(str)

    def write_default_ipaddr(self, ip_var):
        str = "\n"
        str += "var " + ip_var.name + " " + ip_var.type + " = " + "\"127.0.0.1\"\n"
        print(str)

    def write_const_global_func_type_enums(self, xml_funcs, port):
        str = "\nconst (\n"
        for name, func in xml_funcs.items():
            str += (ONE_TAB + func.get_const_func_type_enum_str(port) + " = iota\n")
        str += ")\n"
        print(str)

    def write_call_back_api_typedef(self):
        str = ""
        for func in manager.xml_funcs.values():
            if not func.is_async or not hasattr(func, "callback_api_functype"):
                continue
            str += func.callback_api_functype.get_func_typedef_str()
            str += "\n"
        print(str)

    def write_rpc_client_struct_def(self):
        str = manager.rpc_client.get_declaration_str(capitalize=False)
        print(str)

    def write_interface(self):
        str = manager.global_interface.get_declaration_str()
        print(str)

    def write_async_func_relied_data(self):
        for func in manager.xml_funcs.values():
            if not func.is_ping_internal:
                print(func.request_struct.get_declaration_str())
                print(func.response_struct.get_declaration_str())
            if func.is_async:
                print(func.param_struct.get_declaration_str())
                print(func.get_call_back_func_content_str())

    # FIX: 接口需要优化
    def create_set_ip_addr_func(self, interface_impl):
        func = interface_impl.get_func(FUNC_NAME_SET_IP)
        impl_varname = interface_impl.impl_varname

        str = "func "
        str += func.get_func_signature_with_impl(impl_varname)
        str += " {\n"
        str += ONE_TAB + "cmd_str := \"ping \" + ip + \" -c 1\"\n"
        str += ONE_TAB + "err := exec.Command(\"bash\", \"-c\", cmd_str).Run()\n"
        str += ONE_TAB + "if err != nil {\n"
        str += TWO_TAB + "fmt.Println(\"Go client RPC:Invalid ip address\")\n"
        str += TWO_TAB + "panic(err.Error())\n"
        str += ONE_TAB + "} else {\n"
        str += TWO_TAB + impl_varname.name +".ipaddr = ip\n"
        str += ONE_TAB + "}\n"
        str += "}\n"
        print(str)

    def create_connect_func(self, interface_impl):
        package_name = manager.config.package_name
        default_ip_var_name = manager.default_ipaddr
        func_ping_internal = manager.func_ping_internal
        port = manager.port_content.name
        func = interface_impl.get_func(FUNC_NAME_CONNECT)
        impl_varname = interface_impl.impl_varname

        str = "func "
        str += func.get_func_signature_with_impl(impl_varname)
        str += " {\n"
        str += ONE_TAB + "var err error\n"
        str += ONE_TAB + "var ip_addr string\n"
        str += ONE_TAB + "if len(" + impl_varname.name + ".ipaddr) == 0 {\n"
        str += TWO_TAB + "ip_addr = " + default_ip_var_name.name + "\n"
        str += ONE_TAB + "} else {\n"
        str += TWO_TAB + "ip_addr =" + impl_varname.name + ".ipaddr\n"
        str += ONE_TAB + "}\n"
        str += ONE_TAB + "trace_rpc.PingReqFnType = " + func_ping_internal.const_call_back_func_enum_str + "\n"
        str += ONE_TAB + impl_varname.name + ".client, err = trace_rpc.Dial(ip_addr + \":\" + " + port + ")\n"
        str += ONE_TAB + "if err != nil {\n"
        str += TWO_TAB + "panic(err.Error())\n"
        str += ONE_TAB + "}\n"
        str += "}\n"
        print(str)

    def create_primary_funcs(self):
        self.create_set_ip_addr_func(manager.interface_impl)
        self.create_connect_func(manager.interface_impl)

    def create_xml_funcs(self):
        str = ""
        impl = manager.interface_impl.impl_varname
        for func in manager.xml_funcs.values():
            if func.is_ping_internal:
                continue
            str += func.get_self_func_content_str(impl)
            str += "\n"
        print(str)

    def write_code(self):
        package_name = manager.config.package_name
        port = manager.config.port
        xml_funcs = manager.xml_funcs

        self.write_package_header(package_name)
        self.write_import()
        self.write_port(port, package_name)
        self.write_default_ipaddr(manager.default_ipaddr)
        self.write_const_global_func_type_enums(xml_funcs, port)
        self.write_rpc_client_struct_def()
        self.write_call_back_api_typedef()
        self.write_async_func_relied_data()
        self.write_interface()
        self.create_primary_funcs()
        self.create_xml_funcs()

def help(arg):
    print("need xml path")

def show_import(filename):
    str = "import (\n"

def check_type_dict(var, varname):
    if not type(var) == dict:
        raise TypeError(varname + " must be a dict")

def get_xml_params_info(param):
    check_type_dict(param, "param")
    param_name = param['param_name']
    param_type = param['param_value']
    param_inout = param['param_type']
    return param_name, param_type, param_inout


def show_params(params, params_name):
    print("len of " + params_name + ': ' + str(len(params)))
    for para in params:
        print("")
        print(params_name + ": param_name:" + para["param_name"].capitalize())
        print(params_name + ": param_value:" + para["param_value"])
        print(params_name + ": param_type:" + para["param_type"])
        print("")


def get_xml_func_info(func):
    check_type_dict(func, "func")
    func_name = func['func_name']
    type = func['type']
    subtype = func['subtype']
    pt_params = func['pt_params']
    params = func['params']
    return func_name, type, subtype, pt_params, params


def print_func_info(func):
    print("func_name:" + func['func_name'].capitalize())
    print("type:" + func["type"])
    print("subtype:" + func["subtype"])
    pt_params = func['pt_params']
    params = func['params']
    show_params(pt_params, "pt_params")
    show_params(params, "params")


def show_funcs(funcs):
    print("nums of funcs:" + str(len(funcs)))
    for fun in funcs:
        print_func_info(fun)


global_config = global_config()
manager = global_manager()
writer = code_writer()


def test():
    for func in manager.xml_funcs.values():
        print("async:", func.is_async)
        print("signature:")
        print(func.get_func_signature())
        print("func type str:")
        print(func.get_const_func_type_enum_str("9093"))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        help(sys.argv)
        exit(1)
    funcs, port, client, server, project = lx.load_xml(sys.argv[1])
    namespace = client["namespace"]
    classname = client["classname"]
    filename = client["filename"]
    withping = client["withping"]
    '''
    print("classname:" + classname)
    print("filename:" + filename)
    print("withping:")
    print(withping)
    # show_def(namespace, filename)
    show_import(filename)
    show_funcs(funcs)
    '''
    #print("======================================")

    manager.init_xml_funcs(funcs)
    manager.init_config(port, namespace, filename, withping)
    #manager.show_info()
    writer.init_manager(manager)
    #test()
    #print("-----------------")
    writer.write_code()