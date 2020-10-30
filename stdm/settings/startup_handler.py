import os
import shutil
import traceback
from os.path import expanduser, isfile

from qgis.core import QgsApplication


def copy_startup():
    home = expanduser("~")
    qgs_path = QgsApplication.prefixPath().rstrip('.')
    source = '{}/.qgis2/python/plugins/stdm/settings/startup.py'.format(home)
    source_2 = '{}/python/plugins/stdm/settings/startup.py'.format(qgs_path)
    destination = '{}/.qgis2/python/startup.py'.format(home)
    # Don't copy startup.py if the file exist. To fix file merging issue.
    if os.path.exists(destination):
        return
    try:

        if not isfile(source):
            source = source_2
        if not isfile(destination):
            shutil.copyfile(source, destination)
            return
        source_file = open(source, 'a+')
        destination_file = open(destination, 'a+')
        original_source_lines = source_file.readlines()
        source_lines = map(str.rstrip, original_source_lines)
        original_dest_lines = destination_file.readlines()
        dest_lines = map(str.rstrip, original_dest_lines)
        if source_lines != dest_lines:
            matched_lines = [i for i in original_source_lines
                             if i in original_dest_lines]

            if matched_lines != original_source_lines:
                print >> destination_file, ''
                print >> destination_file, ''
                print >> destination_file, ''
                for line in source_lines:
                    print >> destination_file, line

    except Exception as ex:
        log_config_path = '{}/.qgis2/python/log.txt'.format(home)
        file = open(log_config_path, "a+")
        print >> file, 'Could not copy a file from the source due to an error:' \
                       '\n {}'.format(ex)
        print >> file, traceback.print_exc()
        file.close()
