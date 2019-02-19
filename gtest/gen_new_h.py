#!/usr/bin/python
from sys import argv
import load_xml as lx
import gen_test as gt

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "

def show_def(project, suit_name):
    str = "#ifndef" + BLANK + gt.make_defname(project, suit_name) + "\n"
    str += "#define" + BLANK + gt.make_defname(project, suit_name) + "\n\n"
    return str


def show_include():
    str = "#include <gtest/gtest.h>\n"
    str += "#include <algo/debug.h>\n\n"
    return str


def show_h_head(suit_name):
    str = "class suit_" + suit_name + " : public ::testing::Test\n"
    str += "{\n"
    str += "protected:\n"
    str += ONE_TEB + "void SetUp() override;\n\n"
    str += ONE_TEB + "void TearDown() override;\n\n"
    str += "public:\n"
    return str

def show_h_end(project, suit_name):
    return gt.gen_h_endpart(project, suit_name)

def show_case(case):
    str = ""
    str += ONE_TEB + "int case_" + case["name"] + "();\n"
    return str

def show_cases(cases):
    str = ""
    for case in cases:
        str += show_case(case)
    return str

def show_all(project, suit_name, cases):
    str = ""
    str += show_def(project, suit_name)
    str += show_include()
    str += show_h_head(suit_name)
    str += show_cases(cases)
    str += show_h_end(project, suit_name)
    return str

if __name__ == '__main__':
    project = "iceberg"
    suit_name = "physical_disk"
    cases = [{"name":"0"},{"name":"1"}]
    print show_all(project, suit_name, cases)
