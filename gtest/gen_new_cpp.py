#!/usr/bin/python
from sys import argv
import load_xml as lx
import gen_test as gt

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "

def show_include(suit_name):
    str = "#include \"" + suit_name + ".h\"\n\n"
    return str


def show_fix_func(suit_name):
    str = ""
    str += "void suit_" + suit_name + "::SetUp()\n"
    str += "{\n"
    str += ONE_TEB + "//Implement this if necessary\n"
    str += "}\n\n"

    str += "void suit_" + suit_name + "::TearDown()\n"
    str += "{\n"
    str += ONE_TEB + "//Implement this if necessary\n"
    str += "}\n\n"
    return str

def show_case_func(suit_name, case_name):
    str = "int suit_" + suit_name + "::case_" + case_name + "()\n{\n"
    str += ONE_TEB + "try\n" + ONE_TEB + "{\n"
    str += TWO_TEB + "//FIXME:Implement this if necessary\n"
    str += TWO_TEB + "dbg<<\"case_" + case_name + " \"<<color_green<<\"ok\"<<end_dbg;\n"
    str += ONE_TEB + "} catch(...)\n" + ONE_TEB + "{\n"
    str += TWO_TEB + "dbg << \"case_" + case_name + " \" << color_red << \"faild\" << end_dbgl;\n"
    str += TWO_TEB + "return -1;\n"
    str += ONE_TEB + "}\n"
    str += ONE_TEB + "return 0;\n}\n\n"
    return str

def show_case_def(case_name):
    str = "EXPECT_EQ(0, case_" + case_name + "()); \n"
    return str


def show_cases_def(suit_name, cases):
    str = "TEST_F(suit_" + suit_name + ", suit_" + suit_name + ") \n{\n"
    for case in cases:
        str += show_case_def(case["name"])
    str += "}\n\n"
    return str


def show_case(suit_name, case_name):
    str = show_case_func(suit_name, case_name)
    return str


def show_cases(suit_name, cases):
    str = ""
    for case in cases:
        str += show_case(suit_name, case["name"])
    return str


def show_all(suit_name, cases):
    str = ""
    str += show_include(suit_name)
    str += show_fix_func(suit_name)
    str += show_cases(suit_name, cases)
    str += "//NOTE:PLEASE DO NOT CHANGE THE FOLLOWING\n"
    str += show_cases_def(suit_name, cases)
    return str


if __name__ == '__main__':
    project = "iceberg"
    suit_name = "physical_disk"
    cases = [{"name": "0"}, {"name": "1"}]
    print show_all(suit_name, cases)
