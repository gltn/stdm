import os
import shutil
from datetime import datetime
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QDir

from stdm.data.pg_utils import (
    pg_fix_auto_sequence,
    fetch_with_filter
)

TIME_FORMAT='%Y%m%d%H%M%S%f'

def fix_auto_sequences(table, field):
    seq_query = fetch_with_filter(
        "SELECT pg_get_serial_sequence('{}','{}')".format(
            table,
            field
        )
    )
    if seq_query is None:
        return
    seq_name = seq_query.fetchone()[0]
    pg_fix_auto_sequence(table, seq_name)

def autochange_profile_configfile(new_profilename,current_profilename):
        if new_profilename == '':
            return
        qdir_home_path = QDir.home().path()
        configfile =  qdir_home_path +\
            '/.stdm/configuration.stc'
        #could be changed later to red from key
        autochange_path = qdir_home_path +\
            '/.stdm/_configuration_autochange' 
        if not os.path.exists(autochange_path):
            return
        autochange_path_backup = autochange_path + '/backup'
        if not os.path.exists(autochange_path_backup):
            os.makedirs(autochange_path_backup)
        if current_profilename != '':
            currentprofile_configfile = os.path.join(
                autochange_path,
                current_profilename + '.stc'
            )
            currentprofile_configfile_backup = os.path.join(
                autochange_path_backup,
                current_profilename + '_' +\
                    datetime.now().strftime(TIME_FORMAT) + '.stc'
            )
            if os.path.exists(currentprofile_configfile):
                shutil.copy(
                    currentprofile_configfile,
                    currentprofile_configfile_backup
                )
            shutil.copy(
                configfile,
                currentprofile_configfile
            )

        newprofile_configfile = os.path.join(
            autochange_path,
            new_profilename + '.stc'
        )
        if os.path.exists(newprofile_configfile):
            shutil.copy(
                newprofile_configfile,
                configfile
            )
