#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demonstrate the AST on a simple program."""

# Get the tool:
#   pip install astpretty
#
# See:
#   https://github.com/asottile/astpretty

import ast
import astpretty

astpretty.pprint(ast.parse("""def hello(name):
    return "Hello, {}!".format(name)""").body[0])
