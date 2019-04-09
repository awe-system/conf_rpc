#!/usr/bin/python
from sys import argv


def delete_endline(lines, item):
    is_continue = True
    reverse_del_lines = []
    lines.reverse()
    for line in lines:
        if (is_continue and line.strip() == item):
            is_continue = False
        else:
            reverse_del_lines.append(line)
    reverse_del_lines.reverse()
    return reverse_del_lines


def delete_endempy(lines):
    is_continue = True
    reverse_del_lines = []
    lines.reverse()
    for line in lines:
        if (is_continue and line.strip() == ""):
            continue
        else:
            reverse_del_lines.append(line)
            is_continue = False
    reverse_del_lines.reverse()
    return reverse_del_lines


def make_defname(project_name, suit_name):
    return project_name.upper() + "_" + suit_name.upper() + "_H"


# delete end part
def delete_h_endpart(lines, project_name, suit_name):
    lines = delete_endline(lines, "//NOTE:PLEASE DO NOT CHANGE THE FOLLOWING")
    lines = delete_endline(lines, "};")
    lines = delete_endline(lines, "")
    delline = "#endif //" + make_defname(project_name, suit_name)
    lines = delete_endline(lines, delline)
    lines = delete_endempy(lines)
    return lines


def delete_cpp_def(lines, suit_name):
    line_item = "TEST_F(suit_" + suit_name + ", suit_" + suit_name + ")"
    is_continue = True
    reverse_del_lines = []
    lines.reverse()
    for line in lines:
        if (is_continue and line.strip() != line_item):
            continue
        elif (is_continue and line.strip() == line_item):
            is_continue = False
        else:
            reverse_del_lines.append(line)
    reverse_del_lines.reverse()
    return reverse_del_lines


def delete_cpp_endpart(lines, suit_name):
    lines = delete_cpp_def(lines, suit_name)
    lines = delete_endline(lines, "//NOTE:PLEASE DO NOT CHANGE THE FOLLOWING")
    return lines


def add_h_endpart(lines, project_name, suit_name):
    lines.append("\n//NOTE:PLEASE DO NOT CHANGE THE FOLLOWING\n")
    lines.append("};\n\n")
    newline = "#endif //" + make_defname(project_name, suit_name) + "\n"
    lines.append(newline);
    return lines


def gen_h_endpart(project_name, suit_name):
    lines = add_h_endpart([], project_name, suit_name)
    return showlines(lines)


def find_inlines(lines, dst):
    for line in lines:
        if (line.strip() == dst.strip()):
            return True
    return False


def showlines(lines):
    str = ""
    for line in lines:
        str += line
    return str


def load(fpath):
    try:
        f = open(fpath)
        lines = f.readlines()
        f.close()
        return lines
    except:
        return []


if __name__ == '__main__':
    if len(argv) < 2:
        print "need file"
        exit(1)
    lines = load(argv[1])
    lines = delete_h_endpart(lines, "iceberg", "physical_disk")
    lines = add_h_endpart(lines, "iceberg", "physical_disk")
    showlines(lines)
