#!/usr/bin/python
from sys import argv
import load_xml as lx
import gen_test as gt

BLANK = " "
ONE_TEB = "    "
TWO_TEB = "        "
THREE_TEB = "            "


def show_case(case):
    return ONE_TEB + "int case_" + case["name"] + "();\n"


def add_cases(lines, cases):
    for case in cases:
        caseline = show_case(case)
        if (not gt.find_inlines(lines, caseline)):
            lines.append(caseline)
    return lines


def show_all(fn, project, suit_name, cases):
    lines = gt.load(fn)
    lines = gt.delete_h_endpart(lines, project, suit_name)
    lines = add_cases(lines, cases)
    lines = gt.add_h_endpart(lines, project, suit_name)
    return gt.showlines(lines)


if __name__ == '__main__':
    project = "iceberg"
    suit_name = "physical_disk"
    cases = [{"name": "3"},{"name": "1"}]
    filename = "./tmp.h"
    print show_all(filename, project, suit_name, cases)
