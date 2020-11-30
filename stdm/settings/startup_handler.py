import os
import shutil
import traceback
from os.path import expanduser, isfile

from qgis.core import QgsApplication

from stdm.exceptions import DummyException

def copy_startup():
    home = expanduser("~")
    qgs_path = QgsApplication.prefixPath().rstrip('.')
    source = '{}/python/plugins/stdm/settings/startup.py'.format(QgsApplication.qgisSettingsDirPath())
    source_2 = '{}/python/plugins/stdm/settings/startup.py'.format(qgs_path)
    destination = '{}/python/startup.py'.format(QgsApplication.qgisSettingsDirPath())
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
        source_lines = list(map(str.rstrip, original_source_lines))
        original_dest_lines = destination_file.readlines()
        dest_lines = list(map(str.rstrip, original_dest_lines))
        if source_lines != dest_lines:
            matched_lines = [i for i in original_source_lines
                             if i in original_dest_lines]

            if matched_lines != original_source_lines:
                destination_file.writelines(['', '', ''])
                destination_file.writelines(source_lines)

    except DummyException as ex:
        log_config_path = '{}/python/log.txt'.format(QgsApplication.qgisSettingsDirPath())
        file = open(log_config_path, "a+")
        file.write('Could not copy a file from the source due to an error:' \
                       '\n {}\n'.format(ex))
        file.write(traceback.print_exc())
        file.close()
