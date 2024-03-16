#  Copyright (C) 2023 Maxim Slipenko.
#  
#  This file is part of the python-LimeReport library.
#  
#  The python-LimeReport library is free software; you can redistribute it and/or modify
#  it under the terms of either:
#  
#    * the GNU Lesser General Public License as published by the Free
#      Software Foundation; either version 3 of the License, or (at your
#      option) any later version.
#  
#  or
#  
#    * the GNU General Public License as published by the Free Software
#      Foundation; either version 3 of the License, or (at your option) any
#      later version.
#  
#  or both in parallel, as here.
#  
#  The python-LimeReport library is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#  for more details.
#  
#  You should have received copies of the GNU General Public License and the
#  GNU Lesser General Public License along with the python-LimeReport library. If not,
#  see https://www.gnu.org/licenses/. 
#  

import os
import re
import subprocess
import sys
from pathlib import Path
import platform

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

from wheel.bdist_wheel import bdist_wheel

import shiboken6

USE_ZINT_ENV_KEY = 'LIMEREPORT_USE_ZINT'
USE_ZINT = os.environ.get(USE_ZINT_ENV_KEY, 'False').lower() in ('true', '1', 't')

USE_LIMITED_API_ENV_KEY = 'LIMEREPORT_USE_LIMITED_API'
USE_LIMITED_API = os.environ.get(USE_LIMITED_API_ENV_KEY, 'True').lower() in ('true', '1', 't')

def qt_version_tuple():
    proc = subprocess.Popen(['qmake', '-query', 'QT_VERSION'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    return output.decode('utf-8').strip().split('.')
    
qt_major, qt_minor, qt_patch = qt_version_tuple()
(p_major, p_minor, p_patchlevel) = platform.python_version_tuple()
pyside_version = f"{(2 if qt_major == 5 else qt_major)}"

def get_name():
    n = f"LimeReport-qt-{qt_major}-{qt_minor}"

    if USE_ZINT:
        return n + "-Z"
    
    return n

def get_license():
    if USE_ZINT:
        return "GPLv3"
    else:
        return "LGPLv3"

def get_license_files():
    if USE_ZINT:
        return ["COPYING.gpl3"]
    else:
        return ["COPYING.lgpl3"]

def get_classifiers():
    c = [
        "Environment :: X11 Applications :: Qt",
        "Programming Language :: C++",
        f"Programming Language :: Python :: {p_major}",
        f"Programming Language :: Python :: {p_major}.{p_minor}",
    ]
    
    if USE_ZINT:
        c.append("License :: OSI Approved :: GNU General Public License v3 (GPLv3)")
    else:
        c.append("License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)")

    return c

PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
    "win-arm32": "ARM",
    "win-arm64": "ARM64",
}

class CMakeExtension(Extension):
    def __init__(self, name: str, source_dir: str = "", write_top_level_init = None, py_limited_api = False) -> None:
        super().__init__(
            name=name, 
            sources=[],
            py_limited_api=py_limited_api,
        )
        self.source_dir = os.fspath(Path(source_dir).resolve())
        self.write_top_level_init = write_top_level_init

class BuildExt(build_ext):
    def build_extension(self, ext: CMakeExtension) -> None:
        # Must be in this form due to bug in .resolve() only fixed in Python 3.10+
        ext_fullpath = Path.cwd() / self.get_ext_fullpath(ext.name)
        extdir = ext_fullpath.parent.absolute()


        debug = int(os.environ.get("DEBUG", 0)) if self.debug is None else self.debug
        cfg = "Debug" if debug else "Release"

        cmake_generator = os.environ.get("CMAKE_GENERATOR", "")

        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}{os.sep}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
            f"-DENABLE_ZINT={'ON' if USE_ZINT else 'OFF'}",
            f"-DPython3_EXECUTABLE={sys.executable}"
        ]
        build_args = []
        # Adding CMake arguments set as environment variable
        # (needed e.g. to build for ARM OSx on conda-forge)
        if "CMAKE_ARGS" in os.environ:
            cmake_args += [item for item in os.environ["CMAKE_ARGS"].split(" ") if item]

        if self.compiler.compiler_type != "msvc":
            if not cmake_generator or cmake_generator == "Ninja":
                try:
                    import ninja

                    ninja_executable_path = Path(ninja.BIN_DIR) / "ninja"
                    cmake_args += [
                        "-GNinja",
                        f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}",
                    ]
                except ImportError:
                    pass
        else:
            # Single config generators are handled "normally"
            single_config = any(x in cmake_generator for x in {"NMake", "Ninja"})

            # CMake allows an arch-in-generator style for backward compatibility
            contains_arch = any(x in cmake_generator for x in {"ARM", "Win64"})

            # Specify the arch if using MSVC generator, but only if it doesn't
            # contain a backward-compatibility arch spec already in the
            # generator name.
            if not single_config and not contains_arch:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

            # Multi-config generators have a different way to specify configs
            if not single_config:
                cmake_args += [
                    f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{cfg.upper()}={extdir}"
                ]
                build_args += ["--config", cfg]

        if sys.platform.startswith("darwin"):
            # Cross-compile support for macOS - respect ARCHFLAGS if set
            archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
            if archs:
                cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

        if "CMAKE_BUILD_PARALLEL_LEVEL" not in os.environ:
            if hasattr(self, "parallel") and self.parallel:
                build_args += [f"-j{self.parallel}"]

        build_temp = Path(self.build_temp) / ext.name
        if not build_temp.exists():
            build_temp.mkdir(parents=True)

        subprocess.run(
            ["cmake", ext.source_dir, *cmake_args], cwd=build_temp, check=True
        )
        subprocess.run(
            ["cmake", "--build", ".", *build_args], cwd=build_temp, check=True
        )

        if ext.write_top_level_init is not None:
            with open(file=Path(extdir) / "__init__.py", mode="w") as f:
                f.write(ext.write_top_level_init)

class BDistWheel(bdist_wheel):
    def finalize_options(self):

        if USE_LIMITED_API:
            [s_major, s_minor] = shiboken6.__minimum_python_version__
            self.py_limited_api = f"cp{s_major}{s_minor}"

        return super().finalize_options()

init_py = Path("init.py").read_text()

setup(
    name=get_name(),
    license = get_license(),
    classifiers = get_classifiers(),
    license_files = get_license_files(),
    ext_modules=[
        CMakeExtension(
            name="LimeReport/LimeReport",
            write_top_level_init=init_py,
            source_dir=str(Path(__file__).parent.absolute()),
            py_limited_api=True
        )
    ],
    cmdclass={
        "build_ext": BuildExt,
        "bdist_wheel": BDistWheel,
    },
    install_requires=[
        f"PySide{pyside_version}=={qt_major}.{qt_minor}.*",
        f"shiboken{pyside_version}=={qt_major}.{qt_minor}.*"
    ],
)