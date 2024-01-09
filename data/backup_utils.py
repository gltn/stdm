import gzip
import os
import shutil
import subprocess
import datetime
from datetime import datetime
from datetime import timedelta
from stdm.data.config import DatabaseConfig
from stdm.settings.registryconfig import (
    config_file_name,
    RegistryConfig,
    backup_path,
    pg_bin_path,
    AUTOBACKUP_DATE,
    autobackup_date,
    AUTOBACKUP_KEY,
    autobackup_key,
    AUTOBACKUP_NEXT,
    autobackup_next,
)
from PyQt4.QtGui import(
    QApplication,
    QMessageBox
)
AUTOBACKUP_KEYS = ['Never','Daily','Weekly','Monthly','Each Login']
BACKUP_PRFXDATEFORMAT = '%Y%m%d%H%M%S%f_'
BACKUP_DATEFORMAT = '%d-%m-%Y'


def perform_autobackup():
    key = autobackup_key()
    apn = autobackup_next()
    if key is None:
        return -1
    if key == 'Never':
        return 1
    exec_backup = (key == 'Each Login')
    if not exec_backup:
        if apn is None:
            return -2
        sch_date = datetime.strptime(apn, BACKUP_DATEFORMAT)
        exec_backup = (sch_date <= datetime.now())
        if exec_backup:
            n_sch_date = sch_date
            if key == 'Daily':
                incdays = 1
            if key == 'Weekly':
                incdays = 7
            if key == 'Monthly':
                incdays = 30 
            while n_sch_date <= datetime.now():
                n_sch_date = (n_sch_date + timedelta(days=incdays))
    
    if not exec_backup:
        return 2
    
    if QMessageBox.warning(
            None, 
            "Auto Backup",
            QApplication.translate(
                "Backup",
                "Do You Want to Perform Auto-Backup?"
            ), 
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.No:
        return 3

    datetime_prfx = datetime.now().strftime(BACKUP_PRFXDATEFORMAT)
    config_file = config_file_name()
    backup_out_path = backup_path()
    pgbin_path = pg_bin_path()
    db_conn = DatabaseConfig().read()
    if db_conn is None:
        return -3
    p_host = db_conn.Host
    p_port = db_conn.Port
    p_database = db_conn.Database

    backup_config(datetime_prfx, config_file, backup_out_path)
    backup_database(
        datetime_prfx,
        pgbin_path,
        p_host,
        p_port,
        p_database,
        backup_out_path
    )
    
    last_exec_date = datetime.now().strftime(BACKUP_DATEFORMAT)
    _reg_config = RegistryConfig()
    _reg_config.write({AUTOBACKUP_DATE: last_exec_date})
    if key != 'Each Login':
        _reg_config.write(
            {AUTOBACKUP_NEXT: n_sch_date.strftime(BACKUP_DATEFORMAT)}
        )
    
    return 0

def backup_config(datetime_prfx, config_file, output_path):
    dest_config_file = (output_path
                           + '//bkup_' 
                           + datetime_prfx 
                           + 'configuration.stc')

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    shutil.copy(config_file, dest_config_file)
    return True

def backup_database(datetime_prfx, pgbin_folder,
        p_host, p_port, p_database, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    dest_db_filename = (output_path
                        + '//bkup_' 
                        + datetime_prfx 
                        + p_database 
                        + '.backup')
    cmd_dump = pgbin_folder + '/pg_dump'    
    cmd = cmd_dump + ' -f {} -F c -h {} -U {} -p {} {}'.format(
        dest_db_filename,
        p_host,
        'postgres',
        p_port,
        p_database
    )
        
    with gzip.open(dest_db_filename, 'wb') as f:
        popen = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
    for stdout_line in iter(popen.stdout.readline, ''):
        f.write(stdout_line.encode('utf-8'))
    popen.stdout.close()
    popen.wait()
    popen = None
    
    return True