from __future__ import print_function

import collections
import os
import sys

import pycdlib


def extract_iso(iso_path, path_type, extract_to, start_path):
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
    return 0
