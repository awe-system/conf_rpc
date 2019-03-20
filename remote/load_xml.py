import xml.dom.minidom as dom
import json

def load_func(funcs, func):
    newfunc = {"func_name": func.getAttribute("name"),
               "type": func.getAttribute("type"),
               "subtype":func.getAttribute("subtype")}
    params = []
    for param in func.getElementsByTagName("param"):
        param_item = {"param_name": param.getAttribute("name"),
                      "param_value": param.getAttribute("value"),
                      "param_type": param.getAttribute("type")}
        params.append(param_item)
    newfunc.update({"params": params})
    pt_params = []
    for param in func.getElementsByTagName("param_passthrough"):
        param_item = {"param_name": param.getAttribute("name"),
                      "param_value": param.getAttribute("value"),
                      "param_type": "param_passthrough"}
        pt_params.append(param_item)
    newfunc.update({"pt_params": pt_params})
    funcs.append(newfunc)
    return funcs


def load_port(child):
    port_content = child.getAttribute("content")
    return port_content

def load_project(child):
    project_content = child.getAttribute("content")
    return project_content

def safegetattr(child, key, default):
    try:
        str = child.getAttribute(key)
        if(str == ""):
            return default
        return str
    except:
        return default

def bool_trans(str):
    if str == "true":
        return True
    elif str == "false":
        return False
    else :
        print str


def load_client(child):
    client_type = child.getAttribute("type")
    res = {"type": client_type}
    res.update({"filename": child.getAttribute("filename")})
    res.update({"withping": bool_trans(safegetattr(child,"withping","false"))})
    if client_type == "C++":
        namespace = child.getAttribute("namespace")
        res.update({"namespace": namespace})
        classname = child.getAttribute("classname")
        if(classname == ""):
            classname = namespace
        res.update({"classname": classname})
    return res

def load_server(child):
    server_type = child.getAttribute("type")
    res = {"type": server_type}
    res.update({"filename": child.getAttribute("filename")})
    if server_type == "C++":
        namespace = child.getAttribute("namespace")
        res.update({"namespace": namespace})
        classname = child.getAttribute("classname")
        if(classname == ""):
            classname = namespace
        res.update({"classname": classname})
    return res

def load_function_type(child):
    func_type = child.getAttribute("type")
    res = {"type": func_type}
    res.update({"filename": child.getAttribute("filename")})
    if func_type == "C++":
        namespace = child.getAttribute("namespace")
        res.update({"namespace": namespace})
    return res


def load_xml(filen):
    funcs = []
    port = ""
    client = {}
    server = {}
    project = ""
    d = dom.parse(filen)
    root = d.documentElement
    if root.tagName != "funcs": return er.xmlbadformate
    for child in root.childNodes:
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "func":
            funcs = load_func(funcs, child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "port":
            port = load_port(child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "project":
            project = load_project(child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "client":
            client = load_client(child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "server":
            server = load_server(child)
    if client["withping"]:
        ping_func={"func_name":"ping_internal","type": "sync","pt_params": [],"params": [],"subtype": ""}
        funcs.append(ping_func)
    return funcs, port, client, server, project

if __name__ == '__main__':
    print json.dumps(load_xml("./example.xml"))

