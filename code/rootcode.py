import shutil
import os
import json
import time

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
    mod_package = {}

    mod_package["mod_package_location"] = temp_directory + name + "\\"

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
