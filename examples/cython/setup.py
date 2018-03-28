# -*- coding: utf-8 -*-
#
"""setuptools-based setup.py example for Cython.

Usage:
    python setup.py build_ext --inplace

Build script only, no data for packaging/distribution. Supports Python 3.4+.

For more complete examples, see:
  For FFI with Cython:  https://github.com/thearn/simple-cython-example
  For number-crunching: https://github.com/Technologicat/setup-template-cython
"""

#########################################################
# Configuration - customize this section!
#########################################################

# Declare your Cython extension modules here.
#
ext_module_ssedemo = declare_cython_extension( "sse_demo", use_math=True, use_openmp=False )

# This list is mainly to allow a manual logical ordering of the declared modules.
#
cython_ext_modules = [ext_module_ssedemo]

# Make absolute(-ish) cimports work.
#     https://github.com/cython/cython/wiki/PackageHierarchy
#
my_include_dirs = ["."]

build_type="optimized"
#build_type="debug"

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

# Additional flags to compile/link with OpenMP
#
openmp_compile_args = ['-fopenmp']
openmp_link_args    = ['-fopenmp']

#########################################################
# Helper functions
#########################################################

def declare_cython_extension(extName, use_math=False, use_openmp=False):
    """Declare a Cython extension module for setuptools.

Parameters:
    extName : str
        Absolute module name, e.g. use `mylibrary.mypackage.subpackage`
        for the Cython source file `mylibrary/mypackage/subpackage.pyx`.

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
        compile_args = list(my_extra_compile_args_math) # copy
        link_args    = list(my_extra_link_args_math)
        libraries    = ["m"]  # link libm; this is a list of library names without the "lib" prefix
    else:
        compile_args = list(my_extra_compile_args_nonmath)
        link_args    = list(my_extra_link_args_nonmath)
        libraries    = None  # value if no libraries, see setuptools.extension._Extension

    # OpenMP
    if use_openmp:
        compile_args.insert( 0, openmp_compile_args )
        link_args.insert( 0, openmp_link_args )

    # On linking libraries to your Cython extensions:
    #    http://docs.cython.org/src/tutorial/external.html
    #
    return Extension(extName,
                     [extPath],
                     extra_compile_args=compile_args,
                     extra_link_args=link_args,
                     libraries=libraries)

#########################################################
# Main program
#########################################################

import os
from setuptools import setup
from setuptools.extension import Extension

try:
    from Cython.Build import cythonize
except ImportError:
    from sys import exit
    exit("Cython not found. Cython is needed to build the extension modules.")

if build_type == 'optimized':
    my_extra_compile_args_math    = extra_compile_args_math_optimized
    my_extra_compile_args_nonmath = extra_compile_args_nonmath_optimized
    my_extra_link_args_math       = extra_link_args_math_optimized
    my_extra_link_args_nonmath    = extra_link_args_nonmath_optimized
    my_debug = False
    print( "build configuration selected: optimized" )
elif build_type == 'debug':
    my_extra_compile_args_math    = extra_compile_args_math_debug
    my_extra_compile_args_nonmath = extra_compile_args_nonmath_debug
    my_extra_link_args_math       = extra_link_args_math_debug
    my_extra_link_args_nonmath    = extra_link_args_nonmath_debug
    my_debug = True
    print( "build configuration selected: debug" )
else:
    raise ValueError("Unknown build configuration '%s'; valid: 'optimized', 'debug'" % (build_type))

# Call cythonize() explicitly, as recommended in the Cython documentation:
#     http://cython.readthedocs.io/en/latest/src/reference/compilation.html#compiling-with-distutils
#
# This will favor Cython's own handling of '.pyx' sources over that provided by setuptools.
#
# Note that my_ext_modules is just a list of Extension objects.
# We could also add any C sources (not coming from Cython modules) here if needed.
#
# cythonize() just performs the Cython-level processing, and returns a list of Extension objects.
#
final_ext_modules = cythonize( cython_ext_modules, include_path=my_include_dirs, gdb_debug=my_debug )

# http://setuptools.readthedocs.io/en/latest/setuptools.html
setup(setup_requires = ["cython"],
      install_requires = [],
      ext_modules = final_ext_modules)  # all extension modules (list of Extension objects)

