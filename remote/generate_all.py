import load_xml as lx
import os
from sys import argv


def gen_cplus(xml):
    filename = client["filename"] + "_internal"
    cmd = "python ./generate_client_inter_h.py " + xml + " > ./output/" + filename + ".h"
    print(cmd)
    os.system(cmd)
    cmd = "python ./generate_client_inter_cpp.py " + xml + " > ./output/" + filename + ".cpp"
    print(cmd)
    os.system(cmd)
    filename = client["filename"]
    cmd = "python ./generate_client_h.py " + xml + " > ./output/" + filename + ".h"
    print(cmd)
    os.system(cmd)
    cmd = "python ./generate_client_cpp.py " + xml + " > ./output/" + filename + ".cpp"
    print(cmd)
    os.system(cmd)

def gen_python(xml):
    filename = client["filename"]
    cmd = "python ./generate_client_py.py " + xml + " > ./output/" + filename + ".py"
    print(cmd)
    os.system(cmd)


def gen_client(xml):
    if(client["type"] == "C++"):
        gen_cplus(xml)
    elif (client["type"] == "python"):
        gen_python(xml)
    elif(client["type"] == "python/C++"):
        gen_python(xml)
        gen_cplus(xml)


def gen_server(xml):
    filename = server["filename"]
    cmd = "python ./generate_server_h.py " + xml + " > ./output/" + filename + ".h"
    print(cmd)
    os.system(cmd)
    cmd = "python ./generate_server_cpp.py " + xml + " > ./output/" + filename + ".cpp"
    print(cmd)
    os.system(cmd)


if __name__ == '__main__':
    if len(argv) < 2:
        print("need xml")
        exit(1)
    funcs, port, client, server, project = lx.load_xml(argv[1])
    os.system("mkdir output")
    gen_client(argv[1])
    gen_server(argv[1])
