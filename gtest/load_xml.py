#!/usr/bin/python
from sys import argv
import xml.dom.minidom as dom


def load_project(child):
    return child.getAttribute("name")

def load_suits(suits, child):
    new_suit = {"name": child.getAttribute("name")}
    cases = []
    for case in child.getElementsByTagName("case"):
        case_item = {"name": case.getAttribute("name")}
        cases.append(case_item)
    new_suit.update({"cases": cases})
    suits.append(new_suit)
    return suits

def load_xml(filen):
    d = dom.parse(filen)
    root = d.documentElement
    if root.tagName != "suits": return er.xmlbadformate
    suits = []
    for child in root.childNodes:
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "project":
            porject = load_project(child)
        if root.ELEMENT_NODE == child.nodeType and child.tagName == "suit":
            suits = load_suits(suits, child)
    return porject, suits


if __name__ == '__main__':
    if len(argv) < 2:
        print "need xml"
        exit(1)
    print load_xml(argv[1])
