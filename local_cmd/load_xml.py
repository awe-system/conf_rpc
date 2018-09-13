import xml.dom.minidom as dom


def load_func(funcs, func):
    newfunc = {"func_name": func.getAttribute("name")}
    params = []
    for param in func.getElementsByTagName("param"):
        param_item = {"param_name": param.getAttribute("name"),
                      "param_value": param.getAttribute("value"),
                      "param_type": param.getAttribute("type")}
        params.append(param_item)
    newfunc.update({"params": params})
    funcs.append(newfunc)
    return funcs


def load_sock(child):
    sock = {}
    sock_name = child.getAttribute("name")
    sock_type = child.getAttribute("type")
    sock.update({"name": sock_name})
    sock.update({"type": sock_type})
    return sock


def load_client(child):
    client_type = child.getAttribute("type")
    res = {"type": client_type}
    res.update({"filename": child.getAttribute("filename")})
    if client_type == "C++":
        namespace = child.getAttribute("namespace")
        res.update({"namespace": namespace})
    return res


def load_server(child):
    server_type = child.getAttribute("type")
    res = {"type": server_type}
    res.update({"filename": child.getAttribute("filename")})
    if server_type == "C++":
        namespace = child.getAttribute("namespace")
        res.update({"namespace": namespace})
    return res


def load_xml(filen):
    funcs = []
    sock = {}
    client = {}
    server = {}
    d = dom.parse(filen)
    root = d.documentElement
    if root.tagName != "funcs": return er.xmlbadformate
    for child in root.childNodes:
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "func":
            funcs = load_func(funcs, child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "sock":
            sock = load_sock(child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "client":
            client = load_client(child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "server":
            server = load_server(child)
    return funcs, sock, client, server
