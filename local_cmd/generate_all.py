import load_xml as lx
import os
from sys import argv

global path

def gen_python_client(client, xml):
    filename = client["filename"]
    cmd = "python "+path+"generate_local_python_client.py " + xml + " > ./output/" + filename + ".py"
    print(cmd)
    os.system(cmd)


client_tab = {
    "python": gen_python_client,
}


def gen_client(client, xml):
    client_tab[client["type"]](client, xml);


def gen_cpp_server(server, xml):
    filename = server["filename"]
    cmd = "python "+path+"generate_local_cpp_server_h.py " + xml + " > ./output/" + filename + ".h"
    print(cmd)
    os.system(cmd)
    cmd = "python "+path+"generate_local_cpp_server_cpp.py " + xml + " > ./output/" + filename + ".cpp"
    print(cmd)
    os.system(cmd)


server_tab = {
    "C++": gen_cpp_server,
}


def gen_server(server, xml):
    server_tab[server["type"]](server, xml);


if __name__ == '__main__':
    path = os.path.abspath(argv[0])
    path = os.path.dirname(path) + '/'
    print(path)
    if (len(argv) < 2):
        print("need xml")
        exit(1)

    funcs, sock, client, server = lx.load_xml(argv[1])
    os.system("mkdir output")
    gen_client(client, argv[1])
    gen_server(server, argv[1])
