#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Determine method resolution order (MRO) of classes defined in a given Python source file.

This is simplistic; e.g. no attempt is made to identify which namespace
a class definition resides in, and only a single input file is supported.

Most of this code was originally developed for the Python 3 port of Pyan:

  https://github.com/Technologicat/pyan

so if interested in extending this, maybe have a look at pyan/analyzer.py.

Created on Thu Feb  8 13:37:13 2018

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import argparse
import logging
import ast
from functools import reduce
from operator import add

__version__ = "1.0.0"  # version of this program

# https://en.wikipedia.org/wiki/Abstract_syntax_tree
# https://en.wikipedia.org/wiki/Visitor_pattern
# https://docs.python.org/3/library/ast.html

class MROVisitor(ast.NodeVisitor):
    def __init__(self, filename, logger):
        self.filename = filename
        self.logger   = logger
        self.classes  = {}  # key: class name, value: list of immediate ancestors

    # We are only interested in ClassDef nodes, so this is the only visit_*() we provide.
    def visit_ClassDef(self, node):
        self.logger.debug("Visiting ClassDef node %s" % (node.name))

        self.classes[node.name] = []
        for n in node.bases:
            base_name = get_name(n)
            self.logger.debug("    {:s} is a base of {:s}".format(base_name, node.name))
            self.classes[node.name].append(base_name)

    def run(self):
        self.logger.debug("Reading in input file '{:s}'".format(self.filename))
        with open(self.filename, "rt", encoding="utf-8") as f:
            content = f.read()

        self.logger.debug("Parsing AST")
        self.visit(ast.parse(content, self.filename))

        self.logger.debug("Detected classes and their bases:")
        self.logger.debug(self.classes)

        self.logger.debug("Computing MRO")
        mro = compute_mro(self.classes, self.logger)

        self.logger.debug("Final result")
        self.logger.debug(mro)

def get_name(node):
    """Get the full name of an AST node.

    Name and Attribute nodes are supported. Attributes are resolved recursively.
    """
    if isinstance(node, ast.Attribute):
        obj_node  = node.value  # AST node representing the object this is an attribute of
        obj_name  = get_name(obj_node)
        attr_name = node.attr   # the name of the attribute
        return "{:s}.{:s}".format(obj_name, attr_name)
    elif isinstance(node, ast.Name):
        return node.id
    else:
        raise NotImplementedError('Unsupported node type {:s}'.format(str(type(node))))

def compute_mro(classes, logger):
    """Compute the method resolution order (MRO) for a set of classes,
    using C3 linearization.

    Parameters:
        classes: dict
            cls: [base1, base2, ..., baseN]
                where cls and basej are class names as strings.

    Return value:
        dict: method resolution order for each class in the input.
            cls: [mro1, mro2, ..., mroM]

    See:
        https://en.wikipedia.org/wiki/C3_linearization#Description
    """

    # List utilities

    def head(lst):
        if len(lst):
            return lst[0]

    def tail(lst):
        if len(lst) > 1:
            return lst[1:]
        else:
            return []

    def remove_all(elt, lst):  # remove all occurrences of elt from lst, return a copy
        return [x for x in lst if x != elt]

    def remove_all_in(elt, lists):  # remove elt from all lists, return a copy
        return [remove_all(elt, lst) for lst in lists]

    # Custom exception, to have a distinct type to catch.
    #
    class LinearizationImpossible(Exception):
        pass

    # C3 specific utilities

    def C3_find_good_head(heads, tails):  # find an element of heads which is not in any of the tails
        flat_tails = reduce(add, tails, [])  # flatten the outer level
        for hd in heads:
            if hd not in flat_tails:
                break
        else:  # no break only if there are cyclic dependencies.
            raise LinearizationImpossible("MRO linearization impossible; cyclic dependency detected. heads: %s, tails: %s" % (heads, tails))
        return hd

    def C3_merge(lists):
        out = []
        while True:
            logger.debug("        MRO: C3 merge: out: %s, lists: %s" % (out, lists))
            heads = [head(lst) for lst in lists if head(lst) is not None]
            if not len(heads):
                break
            tails = [tail(lst) for lst in lists]
            logger.debug("        MRO: C3 merge: heads: %s, tails: %s" % (heads, tails))
            hd = C3_find_good_head(heads, tails)
            logger.debug("        MRO: C3 merge: chose head %s" % (hd))
            out.append(hd)
            lists = remove_all_in(hd, lists)
        return out

    mro = {}  # result
    try:
        memo = {}  # caching/memoization
        def C3_linearize(name):  # main routine for linearizer
            logger.debug("    MRO: C3 linearizing {:s}".format(name))
            seen.add(name)
            if name not in memo:
                #  unknown class       or no ancestors
                if name not in classes or not len(classes[name]):
                    memo[name] = [name]
                else:  # known and has ancestors
                    lists = []
                    # linearization of parents...
                    for baseclass_node in classes[name]:
                        if baseclass_node not in seen:
                            lists.append(C3_linearize(baseclass_node))
                    # ...and the parents themselves (in the order they appear in the ClassDef)
                    logger.debug("    MRO: parents of {:s}: {:s}".format(name, str(classes[name])))
                    lists.append(classes[name])
                    logger.debug("    MRO: C3 merging {:s}".format(str(lists)))
                    memo[name] = [name] + C3_merge(lists)  # cache the result
            logger.debug("    MRO: C3 linearized {:s}, result {:s}".format(name, str(memo[name])))
            return memo[name]

        for name in classes:
            logger.debug("MRO: analyzing class {:s}".format(name))
            seen = set()  # break cycles (separately for each class we start from)
            mro[name] = C3_linearize(name)

        return mro
    except LinearizationImpossible as e:
        logger.error(e)
        raise


def main():
    # Let's make a simple command-line interface for the program.
    #
    # Tutorial and API reference:
    #   https://docs.python.org/3/howto/argparse.html
    #   https://docs.python.org/3/library/argparse.html
    #
    desc = ('Determine method resolution order (MRO) in classes defined in a given Python source file.')
    parser = argparse.ArgumentParser(description=desc)

    # named command-line options (help message -h, --help always implicitly provided)
    parser.add_argument('-v', '--version', action='version', version=('%(prog)s ' + __version__) )
    parser.add_argument('-l', '--log', dest='logname', help='write log messages to LOG', metavar='LOG', default=None)

    # positional command-line options
    parser.add_argument('filename', help='Filename of a Python source file (.py) to analyze.')

    # Parse the command line. This will automatically terminate the program if:
    #  - the user asked for -h or -v
    #  - no filename was specified
    #
    args = parser.parse_args()

    # Messages will be printed to sys.stderr (default), and optionally
    # also into a log file.
    #
    # Tutorial and API reference:
    #   https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
    #   https://docs.python.org/3/library/logging.html
    #
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # DEBUG, INFO, WARN, ERROR
    logger.addHandler(logging.StreamHandler())
    if args.logname is not None:
        handler = logging.FileHandler(args.logname)
        logger.addHandler(handler)

    # Start the analyzer.
    #
    m = MROVisitor(args.filename, logger)
    m.run()

if __name__ == '__main__':
    main()
