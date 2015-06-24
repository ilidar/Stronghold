#!/usr/bin/python

import os
import fnmatch


def get_image_paths(root):
    results = []
    for root, dirnames, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, '*.png'):
            if "@" not in filename:
                results.append(os.path.join(root, filename))
    return results


def get_tree(root):
    tree = {root: []}
    for image_path in get_image_paths(root):
        parent = root
        for node in image_path.split("/"):
            children = tree.get(parent)
            if children is not None:
                if node not in children:
                    children.append(node)
            else:
                tree[parent] = []
            parent = node
    return tree


def get_indent(level, tab_size=4):
    return " " * (level * tab_size)


def get_node(root, level):
    return '%spublic static readonly String %s = "%s";' % \
        (get_indent(level), "X", root)


def get_properties(nodes, level):
    return ""
    result = ""
    for node in nodes:
        result += get_node(node, level)
        result += "\n"
    return result


def get_enum(key, values, level):
    indent = get_indent(level)
    name = key.replace("_", " ").title().replace(" ", "")
    result = "%spublic enum %sState\n%s{\n" % (indent, name, indent)
    for value in values:
        result += get_indent(level + 1) + value.title() + ","
        result += "\n"
    result = result[:-2] + "\n"
    result += "%s}\n" % indent
    return result


def get_method_head(key, values, level):
    name = key.replace("_", " ").title().replace(" ", "")
    return "public static File Get%sFile(%sState state)" % (name, name)


def get_method_body(key, values, level):
    indent = get_indent(level)
    result = ""
    result += "%sswitch(state)\n%s{\n" % (indent, indent)
    for value in values:
        result += "%scase %s:\n" \
            % (get_indent(level + 1), value.title())
        result += "%sreturn \"%s\";\n" \
            % (get_indent(level + 2), key + "-" + value)
    result += "%s}" % (indent)
    return result


def get_method(key, values, level):
    indent = get_indent(level)
    head = get_method_head(key, values, level)
    body = get_method_body(key, values, level + 1)
    return "%s%s\n%s{\n%s\n%s}" % \
        (indent, head, indent, body, indent)


def get_methods(nodes, level):
    methods = [node for node in nodes if "-" in node]
    methods_group = {}
    for method in methods:
        name, extension = os.path.splitext(method)
        parts = name.split("-")
        head = parts[0]
        tail = parts[1]
        states = methods_group.get(head)
        if not states:
            methods_group[head] = [tail]
        elif tail not in states:
            states.append(tail)
    result = ""
    for key, values in methods_group.iteritems():
        result += get_enum(key, values, level)
        result += get_method(key, values, level)
        result += "\n"
    return result


def get_class(root, tree, level):
    leafs = []
    sub_trees = []
    for node in tree.get(root):
        if node != root:
            if not tree.get(node):
                leafs.append(node)
            else:
                sub_trees.append(node)
    # flatten to subtree
    if len(leafs) == 0 and len(sub_trees) == 1:
        return get_class(sub_trees[0], tree, level)
    indent = get_indent(level)
    result = "%spublic static class %s\n%s{\n" % (indent, root, indent)
    for node in sub_trees:
        result += get_class(node, tree, level + 1)
        result += "\n"
    result += get_properties(leafs, level + 1)
    result += get_methods(leafs, level + 1)
    result += indent + "}"
    return result


def get_source(root_name, root, tree):
    result = "public static class %s\n{\n" % root_name
    for node in tree.get(root):
        if node != root:
            result += get_class(node, tree, 1)
    result += "\n}"
    return result


print "Working in [%s]..." % (os.getcwd())

root = "."
tree = get_tree(root)
source = get_source("Images", root, tree)
output_file = open("Images.cs", "w")
output_file.write(source)
output_file.close()

print "Done."
