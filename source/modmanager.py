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
    """

    Sets the temporary directory to use for this mod manager instance.

    :param location: A file path to set the temporary directory to.
    :return: Nothing

    """

    global temp_directory
    temp_directory = location


def remove_temporary_directory():
    """

    Deletes the temporary directory and all of its contents.

    :return: Nothing

    """

    global temp_directory
    shutil.rmtree(temp_directory)


def clear_temporary_directory():
    """

    Clears the contents of the temporary directory.

    :return: Nothing

    """

    global temp_directory
    shutil.rmtree(temp_directory, ignore_errors=True)
    try:
        os.mkdir(temp_directory)
    except:
        pass


def unpackage_mod_file(mod_file, name):
    """

    Unpackages a mod file into the current temporary directory,
    and parses its contents.

    :param mod_file: The path to a mod file.
    :param name: The name of the folder to extract the mod into. This folder will be created as a subdirectory in the active temporary folder.

    :return: A dictionary containing this mod's data.

    """

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
    """

    Unpackages an ISO file into the current temporary directory.

    :param iso_path: The path to an ISO file.
    :param name: The name of the folder to extract the ISO into. This folder will be created as a subdirectory in the active temporary folder.
    :param path_type: The type of ISO. Can be auto, iso_path, udf_path, rr_path, or joliet_path.
    :param start_path: The start path to extract the ISO from. This should almost *always* be set to "/".

    :return: The location to the sub directory the ISO was extracted to.

    """
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
    iso.write()
    iso.close()
    return extract_to

'''
def package_iso(unpacked_iso_path, previous_iso=None):
    iso = pycdlib.PyCdlib()
    if previous_iso:
        iso.open(previous_iso)
    else:
        iso.new()

    for entry in os.scandir(unpacked_iso_path):
        if os.path.isdir(entry.path):
            try:
                print("adding directory: " + entry.name)
                iso.add_directory("/" + entry.name.upper())
            except:
                pass

    for entry in os.scandir(unpacked_iso_path):
        if os.path.isfile(entry.path):
            location = os.path.relpath(entry.path, unpacked_iso_path)
            print("adding file: " + entry.name + " path " + location)
            iso.add_file(entry.path, location)

        print(entry.name)
    iso.write("final.iso")
    iso.close()
'''