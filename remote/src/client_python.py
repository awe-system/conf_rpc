#!/usr/bin/python3
import codecs
import json
import socket
import os
from sys import argv
import sys
import subprocess

color_red='\033[1;31;20m'
color_green='\033[1;32;20m'
color_yellow='\033[1;33;20m'
color_blue='\033[1;34;20m'
color_purple='\033[1;35;20m'
color_cyan='\033[1;36;20m'
color_reset='\033[0m'

choice=0
def print_colorfully():
    global choice
    choice += 1
    curchoice = choice % 6
    if(curchoice == 0):
        print(color_red)
    elif(curchoice == 1):
        print(color_green)
    elif(curchoice == 2):
        print(color_yellow)
    elif (curchoice == 3):
        print(color_blue)
    elif (curchoice == 4):
        print(color_purple)
    else:
        print(color_cyan)

max_rcv_len = 256* 1024*1024


class lt_data_t(object):
    len = 0
    buf = bytes()

    def from_len_buf(self, _len, _buf):
        self.len = _len
        self.buf = _buf

    def from_bytes(self, _bytes):
        if(len(_bytes) < size_of_ulong()): return
        self.len = to_unlong(_bytes)
        self.from_len_buf(self.len, _bytes[size_of_ulong():])

    def get_buf(self):
        newbuf = (self.len).to_bytes(size_of_ulong(), 'little')
        newbuf += self.buf
        return newbuf

    def read_from_file(self, fname):
        with open(fname, 'rb') as file_object:
            self.buf = file_object.read()
            file_object.close()
        self.len = len(self.buf)

    def write_to_file(self, fname):
        with open(fname, 'wb') as file_object:
            file_object.write(self.buf)
            file_object.close()

################################################################################
def size_of_string(val):
    return len(val) + 1

def size_of_char_p(val):
    return len(val) + 1

def size_of_ulong():
    return 8

def size_of_uint():
    return 4

def size_of_bool():
    return 1

def size_of_void_p():
    return 8

def size_of_data(val):
    return size_of_ulong() + val.len
#####################################################################################
def by_uint(val):
    return (val).to_bytes(size_of_uint(), 'little')

def by_ulong(val):
    return (val).to_bytes(size_of_ulong(), 'little')

def by_bool(val):
    return (val).to_bytes(size_of_bool(), 'little')

def by_void_p(val):
    return (val).to_bytes(size_of_void_p(), 'little')

def by_string(val):
    return str.encode(val) + (0).to_bytes(1,'little')

def by_char_p(val):
    return by_string(val)

def by_data(val):
    return val.get_buf()
################################################################################
def to_unlong(val):
    tmp_val = bytes()
    i = 0
    for b in val:
        if (i < size_of_ulong()):
            tmp_val += b.to_bytes(1,'little')
        else:
            break
        i = i+1
    return int.from_bytes(tmp_val, 'little')


def to_uint(val):
    tmp_val = bytes()
    i = 0
    for b in val:
        if (i < size_of_uint()):
            tmp_val += b.to_bytes(1,'little')
        else:
            break
        i = i+1
    return int.from_bytes(tmp_val, 'little')


def to_bool(val):
    tmp_val = bytes()
    i = 0
    for b in val:
        if (i < size_of_bool()):
            tmp_val += b.to_bytes(1,'little')
        else:
            break
        i = i+1
    return bool.from_bytes(tmp_val, 'little')

def to_void_p(val):
    return to_unlong(val)

def to_string(val):
    tmp_bytes = bytes()
    for b in val:
        if (b != 0):
            tmp_bytes += (b).to_bytes(1,'little')
        else:
            break
    return tmp_bytes.decode()

def to_char_p(val):
    return to_string(val)

def to_data(val):
    data = lt_data_t()
    data.from_bytes(val)
    return data
################################################################################

def from_arg_unlong(arg):
    return int(arg)

def from_arg_uint(arg):
    return int(arg)

def from_arg_bool(arg):
    if (arg == "0"  or arg == "false" or arg == "False" or arg == "FALSE"):
        return False
    elif (arg == "1" or arg == "true" or arg == "True" or arg == "TRUE" ):
        return True
    else:
        raise

def from_arg_void_p(arg):
    return int(arg)

def from_arg_string(arg):
    return arg

def from_arg_char_p(arg):
    return arg

file_tab = {}

def from_arg_indata(arg,val_name):
    data = lt_data_t()
    data.read_from_file(arg)
    file_tab[val_name] = arg
    return data

def from_arg_outdata(arg,val_name):
    file_tab[val_name] = arg
    return arg

def from_arg_inoutdata(arg,val_name):
    return from_arg_indata(arg, val_name)

################################################################################
#返回一个可以用json.dumps的字典
def to_screen_unlong(out_dic, val_name):
    return {val_name:out_dic[val_name]}

def to_screen_uint(out_dic, val_name):
    return {val_name:out_dic[val_name]}

def to_screen_bool(out_dic, val_name):
    return {val_name: out_dic[val_name]}

def to_screen_void_p(out_dic, val_name):
    return {val_name:out_dic[val_name]}

def to_screen_string(out_dic, val_name):
    return {val_name:out_dic[val_name]}

def to_screen_char_p(out_dic, val_name):
    return {val_name:out_dic[val_name]}

def to_screen_data(out_dic, val_name):
    out_dic[val_name].write_to_file(file_tab[val_name])
    return {val_name:file_tab[val_name]}

################################################################################

