#!/usr/bin/python
from sys import argv
import load_xml as lx
import gen_test as gt
import gen_new_cpp as gnc

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "

def show_case(lines, suit_name, case_name):
    lines.append(gnc.show_case(suit_name, case_name))
    return lines

def add_cases(lines, suit_name, cases):
    for case in cases:
        caseline =  "int suit_" + suit_name + "::case_" + case["name"] + "()"
        if (not gt.find_inlines(lines, caseline)):
            lines = show_case(lines, suit_name, case["name"])
    return lines


def show_all(fn, suit_name, cases):
    lines = gt.load(fn)
    lines = gt.delete_cpp_endpart(lines, suit_name)
    lines = add_cases(lines,suit_name, cases)
    str = gt.showlines(lines)
    str += "//NOTE:PLEASE DO NOT CHANGE THE FOLLOWING\n"
    str += gnc.show_cases_def(suit_name, cases)
    return str


if __name__ == '__main__':
    project = "iceberg"
    suit_name = "physical_disk"
    cases = [{"name": "3"},{"name": "1"},{"name": "4"}]
    filename = "./tmp.cpp"
    print show_all(filename, suit_name, cases)
