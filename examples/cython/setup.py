#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""setuptools-based setup.py example for Cython.

Usage:
    python setup.py build_ext --inplace

Build script only, no data for packaging/distribution. Supports Python 3.4+.

For more complete examples, see:
  For FFI with Cython:  https://github.com/thearn/simple-cython-example
  For number-crunching: https://github.com/Technologicat/setup-template-cython

@author: Juha Jeronen <juha.jeronen@tut.fi>
"""

import os
from setuptools import setup
from setuptools.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError:
    from sys import exit
    exit("Cython not found. Cython is needed to build the extension modules.")

#########################################################
# Configuration
#########################################################

# This is one possible solution to set up a build configuration.
# Customize __init__() and declare_cython_modules() as needed.

class Configuration:
    def __init__(self):
        self.build_type="optimized"
        #self.build_type="debug"

        # Make absolute(-ish) cimports work.
        #     https://github.com/cython/cython/wiki/PackageHierarchy
        #
        self.my_include_dirs = ["."]

        # Base set of compiler and linker flags.
        #
        # This is geared toward x86_64, see
        #    https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html
        #
        # Customize these as needed.
        #
        # Note that -O3 may on rare occasion cause mysterious problems, so we limit ourselves to -O2.

        # Modules involving numerical computations
        #
        extra_compile_args_math_optimized    = ['-march=native', '-O2', '-msse', '-msse2', '-mfma', '-mfpmath=sse']
        extra_compile_args_math_debug        = ['-march=native', '-O0', '-g']
        extra_link_args_math_optimized       = []
        extra_link_args_math_debug           = []

        # Modules that do not involve numerical computations
        #
        extra_compile_args_nonmath_optimized = ['-O2']
        extra_compile_args_nonmath_debug     = ['-O0', '-g']
        extra_link_args_nonmath_optimized    = []
        extra_link_args_nonmath_debug        = []

        if self.build_type == 'optimized':
            self.extra_compile_args_math    = extra_compile_args_math_optimized
            self.extra_compile_args_nonmath = extra_compile_args_nonmath_optimized
            self.extra_link_args_math       = extra_link_args_math_optimized
            self.extra_link_args_nonmath    = extra_link_args_nonmath_optimized
            self.debug = False
            print( "build configuration selected: optimized" )
        elif self.build_type == 'debug':
            self.extra_compile_args_math    = extra_compile_args_math_debug
            self.extra_compile_args_nonmath = extra_compile_args_nonmath_debug
            self.extra_link_args_math       = extra_link_args_math_debug
            self.extra_link_args_nonmath    = extra_link_args_nonmath_debug
            self.debug = True
            print( "build configuration selected: debug" )
        else:
            raise ValueError("Unknown build configuration '%s'; valid: 'optimized', 'debug'" % (self.build_type))

        # Additional flags to compile/link with OpenMP
        #
        self.openmp_compile_args = ['-fopenmp']
        self.openmp_link_args    = ['-fopenmp']

        self.declare_cython_modules()

    def declare(self, extName, use_math=False, use_openmp=False):
        """Declare a Cython extension module for setuptools.

Parameters:
    extName : str
        Absolute module name, e.g. use `mylibrary.mypackage.subpackage`
        for the Cython source file `mylibrary/mypackage/subpackage.pyx`.

    cfg : Configuration
        As returned by config().

    use_math : bool
        If True, set math flags and link with ``libm``.

    use_openmp : bool
        If True, compile and link with OpenMP.

Return value:
    Extension object
        that can be passed to ``setuptools.setup``.
"""
        extPath = extName.replace(".", os.path.sep) + ".pyx"

        if use_math:
            compile_args = self.extra_compile_args_math.copy()
            link_args    = self.extra_link_args_math.copy()
            libraries    = ["m"]  # link libm; this is a list of library names without the "lib" prefix
        else:
            compile_args = self.extra_compile_args_nonmath.copy()
            link_args    = self.extra_link_args_nonmath.copy()
            libraries    = None  # value if no libraries, see setuptools.extension._Extension

        # OpenMP
        if use_openmp:
            compile_args = self.openmp_compile_args + compile_args
            link_args    = self.openmp_link_args    + link_args

        # On linking libraries to your Cython extensions:
        #    http://docs.cython.org/src/tutorial/external.html
        #
        return Extension(extName,
                         [extPath],
                         extra_compile_args=compile_args,
                         extra_link_args=link_args,
                         libraries=libraries)

    def declare_cython_modules(self):
        # Declare your Cython extension modules here.
        #
        ddot     = self.declare("ddot",         use_math=False, use_openmp=False)  # lecture 8, slide 5
        dgemm    = self.declare("dgemm",        use_math=False, use_openmp=False)  # lecture 8, slide 6
        nocopy   = self.declare("nocopy",       use_math=False, use_openmp=False)  # lecture 8, slide 7
        cddot    = self.declare("cddot",        use_math=False, use_openmp=False)  # lecture 8, slide 8
        pdgemm   = self.declare("pdgemm",       use_math=False, use_openmp=True)   # lecture 8, slide 10
        mysum    = self.declare("mysum",        use_math=False, use_openmp=False)  # lecture 8, slide 13
        mysumt   = self.declare("mysum_test",   use_math=False, use_openmp=False)  # lecture 8, slide 13
        ptrwrap  = self.declare("ptrwrap",      use_math=False, use_openmp=False)  # lecture 8, slide 14
        ptrwrapt = self.declare("ptrwrap_test", use_math=False, use_openmp=False)  # lecture 8, slide 14

        # This list is mainly to allow a manual logical ordering of the declared modules.
        #
        self.cython_ext_modules = [ddot, dgemm, nocopy, cddot, pdgemm,
                                   mysum, mysumt,
                                   ptrwrap, ptrwrapt]

#########################################################
# Main program
#########################################################

def main():
    cfg = Configuration()

    # Call cythonize() explicitly, as recommended in the Cython documentation:
    #     http://cython.readthedocs.io/en/latest/src/reference/compilation.html#compiling-with-distutils
    #
    # This will favor Cython's own handling of '.pyx' sources over that provided by setuptools.
    #
    # (It also implies the Cython compilation step will run before setuptools even sees the command-line arguments,
    #  so don't go grab your coffee before Cython finishes!)
    #
    # cythonize() just performs the Cython compile step, and returns a list of Extension objects.
    # We could also add any C sources (not coming from Cython modules) to that list if needed.
    #
    final_ext_modules = cythonize( cfg.cython_ext_modules, include_path=cfg.my_include_dirs, gdb_debug=cfg.debug )

    # http://setuptools.readthedocs.io/en/latest/setuptools.html
    setup(setup_requires = ["cython"],
          install_requires = [],
          ext_modules = final_ext_modules)  # all extension modules (list of Extension objects)

if __name__ == '__main__':
    main()
else:
    print("setup.py is intended to be run as a main program.")
