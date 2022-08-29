# -*- coding=utf-8 -*-
import os
import re
import site
import subprocess
import sys

from setuptools import Extension, setup
from wheel.bdist_wheel import bdist_wheel

from distutils.command.build_py import build_py  # type: ignore   isort: skip
from distutils.command.build_ext import build_ext  # type: ignore   isort: skip
from distutils.command.install import install as distutils_install  # type: ignore   isort: skip

try:
    import cmake

    CMAKE_EXECUTABLE = os.path.join(cmake.CMAKE_BIN_DIR, "cmake")

except ImportError:
    CMAKE_EXECUTABLE = "cmake"

try:
    import ninja

    NINJA_EXECUTABLE = os.path.join(ninja.BIN_DIR, "ninja")
except ImportError:
    NINJA_EXECUTABLE = "ninja"


# workaround https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

# Read the version from chemfiles/__init__.py without importing chemfiles
ROOT = os.path.realpath(os.path.dirname(__file__))
__version__ = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', open("src/chemfiles/__init__.py").read()
).group(1)


class universal_wheel(bdist_wheel):
    # Workaround until https://github.com/pypa/wheel/issues/185 is resolved
    def get_tag(self):
        tag = bdist_wheel.get_tag(self)
        return ("py2.py3", "none") + tag[2:]


class cmake_configure(build_py):
    """configure cmake to build chemfiles and generate external.py"""

    def run(self):
        source_dir = ROOT
        build_dir = os.path.join(ROOT, "build", "cmake-build")
        install_dir = os.path.join(os.path.realpath(self.build_lib))

        try:
            os.makedirs(build_dir)
        except OSError:
            pass

        cmake_options = [
            "-GNinja",
            f"-DCMAKE_MAKE_PROGRAM={NINJA_EXECUTABLE}",
            f"-DCMAKE_INSTALL_PREFIX={install_dir}",
            "-DCMAKE_BUILD_TYPE=Release",
            "-DBUILD_SHARED_LIBS=ON",
        ]

        if sys.platform.startswith("darwin"):
            cmake_options.append("-DCMAKE_OSX_DEPLOYMENT_TARGET:STRING=10.9")

        if os.getenv("CHFL_PY_INTERNAL_CHEMFILES"):
            cmake_options.append("-DCHFL_PY_INTERNAL_CHEMFILES=ON")

        ninja_args = []

        subprocess.run(
            [CMAKE_EXECUTABLE, source_dir, *cmake_options],
            cwd=build_dir,
            check=True,
        )

        return super().run()


class cmake_build(build_ext):
    """build and install chemfiles with cmake"""

    def run(self):
        source_dir = ROOT
        build_dir = os.path.join(ROOT, "build", "cmake-build")

        subprocess.run(
            [CMAKE_EXECUTABLE, "--build", build_dir, "--target", "install"],
            check=True,
        )


install_requires = ["numpy"]
if sys.hexversion < 0x03040000:
    install_requires.append("enum34")


def _get_lib_ext():
    if sys.platform.startswith("win32"):
        ext = ".dll"
    elif sys.platform.startswith("darwin"):
        ext = ".dylib"
    elif sys.platform.startswith("linux"):
        ext = ".so"
    else:
        raise Exception("Unknown operating system: %s" % sys.platform)
    return ext


setup(
    version=__version__,
    install_requires=install_requires,
    ext_modules=[
        # only declare the extension, it is built & copied as required by cmake
        # in the build_ext command
        Extension(name="chemfiles", sources=[]),
    ],
    cmdclass={
        "build_py": cmake_configure,
        "build_ext": cmake_build,
        "bdist_wheel": universal_wheel,
        # HACK: do not use the new setuptools install implementation, it tries
        # to install the package with `easy_install`, which fails to resolve the
        # freshly installed package and tries to load it from pypi.
        "install": distutils_install,
    },
    exclude_package_data={
        "chemfiles": [
            "include/*",
        ]
    },
)
