from __future__ import print_function

import shutil
import os
import json
import time

import collections
import os
import sys

import pycdlib

temp_directory = None


def set_temporary_directory(location):
    global temp_directory
    temp_directory = location


def remove_temporary_directory():
    global temp_directory
    shutil.rmtree(temp_directory)


def clear_temporary_directory():
    global temp_directory
    shutil.rmtree(temp_directory, ignore_errors=True)
    try:
        os.mkdir(temp_directory)
    except:
        pass


def unpackage_mod_file(mod_file, name):
    mod_package = {"mod_package_location": temp_directory + name + "\\"}

    shutil.unpack_archive(mod_file, mod_package["mod_package_location"], "zip")

    mod_package["mod_data"] = mod_package["mod_package_location"] + "data.json"
    mod_package["mod_posdata"] = mod_package["mod_package_location"] + "positions.json"
    mod_package["mod_files"] = mod_package["mod_package_location"] + "files\\"

    with open(mod_package["mod_data"] , 'r') as mod_package["mod_data_file"]:
        mod_package["mod_data_json_u"] = mod_package["mod_data_file"].read()

    with open(mod_package["mod_posdata"], 'r') as mod_package["mod_posdata_file"]:
        mod_package["mod_posdata_json_u"] = mod_package["mod_posdata_file"].read()

    mod_package["mod_data_json"] = json.loads(mod_package["mod_data_json_u"])
    mod_package["mod_posdata_json"] = json.loads(mod_package["mod_posdata_json_u"])

    return mod_package


def unpackage_iso(iso_path, name, path_type="auto", start_path="/"):
    extract_to = temp_directory + name + "\\"
    iso = pycdlib.PyCdlib()
    print('Opening %s' % iso_path)
    iso.open(iso_path)

    if path_type == 'auto':
        if iso.has_udf():
            pathname = 'udf_path'
        elif iso.has_rock_ridge():
            pathname = 'rr_path'
        elif iso.has_joliet():
            pathname = 'joliet_path'
        else:
            pathname = 'iso_path'
    elif path_type == 'rockridge':
        if not iso.has_rock_ridge():
            print('Can only extract Rock Ridge paths from a Rock Ridge ISO')
            return 1
        pathname = 'rr_path'
    elif path_type == 'joliet':
        if not iso.has_joliet():
            print('Can only extract Joliet paths from a Joliet ISO')
            return 2
        pathname = 'joliet_path'
    elif path_type == 'udf':
        if not iso.has_udf():
            print('Can only extract UDF paths from a UDF ISO')
            return 3
        pathname = 'udf_path'
    else:
        pathname = 'iso_path'

    print("Using path type of '%s'" % (pathname))

    root_entry = iso.get_record(**{pathname: start_path})

    dirs = collections.deque([root_entry])
    while dirs:
        dir_record = dirs.popleft()
        ident_to_here = iso.full_path_from_dirrecord(dir_record,
                                                     rockridge=pathname == 'rr_path')
        relname = ident_to_here[len(start_path):]
        if relname and relname[0] == '/':
            relname = relname[1:]
        print(relname)
        if dir_record.is_dir():
            if relname != '':
                os.makedirs(os.path.join(extract_to, relname))
            child_lister = iso.list_children(**{pathname: ident_to_here})

            for child in child_lister:
                if child is None or child.is_dot() or child.is_dotdot():
                    continue
                dirs.append(child)
        else:
            if dir_record.is_symlink():
                fullpath = os.path.join(extract_to, relname)
                local_dir = os.path.dirname(fullpath)
                local_link_name = os.path.basename(fullpath)
                old_dir = os.getcwd()
                os.chdir(local_dir)
                os.symlink(dir_record.rock_ridge.symlink_path(), local_link_name)
                os.chdir(old_dir)
            else:
                iso.get_file_from_iso(os.path.join(extract_to, relname), **{pathname: ident_to_here})

    iso.close()
    return extract_to

def package_iso(unpacked_iso_path):
    iso = pycdlib.PyCdlib()
    iso.new()
    for entry in os.scandir(unpacked_iso_path):
        if os.path.isdir(entry.path):
            print("adding directory: " + entry.name)
            iso.add_directory("/" + entry.name.upper())

    for entry in os.scandir(unpacked_iso_path):
        if os.path.isfile(entry.path):
            location = os.path.relpath(entry.path, unpacked_iso_path)
            print("adding file: " + entry.name + " path " + location)
            iso.add_file(entry.name.upper(), location)

        print(entry.name)
    iso.write("final.iso")
    iso.close()