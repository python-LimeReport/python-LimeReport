#!/usr/bin/env python3
####
# Copyright (C) 2023 Maxim Slipenko.
# 
# This file is part of the python-LimeReport library.
# 
# The python-LimeReport library is free software; you can redistribute it and/or modify
# it under the terms of either:
# 
#   * the GNU Lesser General Public License as published by the Free
#     Software Foundation; either version 3 of the License, or (at your
#     option) any later version.
# 
# or
# 
#   * the GNU General Public License as published by the Free Software
#     Foundation; either version 3 of the License, or (at your option) any
#     later version.
# 
# or both in parallel, as here.
# 
# The python-LimeReport library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
# 
# You should have received copies of the GNU General Public License and the
# GNU Lesser General Public License along with the python-LimeReport library. If not,
# see https://www.gnu.org/licenses/. 
####

import subprocess
import os
import sys
import fileinput

current_dir = os.path.dirname(os.path.realpath(__file__))
SETUP_CFG_PATH = os.path.join(current_dir, "../setup.cfg")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def git_o(*args):
    return subprocess.check_output(['git'] + list(args),  encoding='UTF-8').strip()

def git(*args):
    return subprocess.check_call(['git'] + list(args))

def get_last_tag():
    return git_o("describe", "--tags", git_o("rev-list","--tags", "--max-count=1")).lstrip("v")

def get_version_from_setup_cfg():
    with open(SETUP_CFG_PATH, encoding="utf-8") as f:
        for index, line in enumerate(f):
            if line.startswith("version"):
                return line.split("=")[1].strip()
        
    raise "Cannot find version from setup.cfg"

def modify_version_setup_cfg(version):
    for line in fileinput.input(SETUP_CFG_PATH, inplace=True):
        if (line.startswith("version")):
            print(f'version = {version}')
        else:
            print(line, end='')
        

def bump_semver_suffix(suffix, type):
    release_number = int(suffix.removeprefix(type))
    release_number += 1
    return (type + str(release_number))

def main():
    git("fetch", "--all", "--tag")
    last_tag = get_last_tag()
    version = get_version_from_setup_cfg()
    
    if last_tag != version:
        eprint(f"Last tag didn't match version ({last_tag} != {version})")
        sys.exit(1)
    
    print("Current version:", version)

    parts = version.split(".")
    if len(parts) == 3:
        parts += ["post1"]
    else:
        semver_suffix = parts[3]

        if semver_suffix.startswith("post"):
            semver_suffix = bump_semver_suffix(semver_suffix, "post")
        elif semver_suffix.startswith("dev"):
            semver_suffix = bump_semver_suffix(semver_suffix, "dev")
        else:
            eprint("Unknown version suffix")
            sys.exit(2)

        parts[3] = semver_suffix

    new_version = ".".join(parts)

    print("New version:", new_version)

    modify_version_setup_cfg(new_version)
    git("add", ".")
    git("commit", "-am", "chore: bump version")
        

if __name__ == "__main__":
    main()