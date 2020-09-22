# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Database Backup
Description          : Backs up the STDM database.
Date                 : 10/January/2017
copyright            : (C) 2017 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import csv
import os
import sys

import stat

import datetime
from PyQt4.QtGui import QDesktopServices
from sqlalchemy.sql.expression import text

from sqlalchemy import MetaData
from stdm import _execute, pg_views, pg_tables

home = QDesktopServices.storageLocation(
            QDesktopServices.HomeLocation
        )


def db_to_csv():
    file_path = '{}/.stdm/db_backup/'.format(home)
    if not os.path.isdir(file_path):
        os.makedirs(os.path.dirname(file_path))

        statistics = os.stat(file_path)
        os.chmod(file_path, statistics.st_mode | stat.S_IEXEC)
        os.chmod(file_path, 0777)

    for table in pg_tables():
        backup_path = '{}/{}.csv'.format(file_path, table)
        out_file = open(backup_path, 'wb')
        out_csv = csv.writer(out_file)

        f = open(backup_path, 'wb')

        sql = 'SELECT * FROM {}'.format(table)

        result = _execute(sql)
        cursor = result.cursor

        out_csv.writerow([x[0] for x in cursor.description])

        out_csv.writerows(cursor.fetchall())
        f.close()


def csv_to_db():
    file_path = '{}/.stdm/db_backup/'.format(home)

    for table in pg_tables():
        csv_path = '{}/{}.csv'.format(file_path, table)
        sql = "COPY {0} FROM '{1}' DELIMITER ',' CSV HEADER".format(table, csv_path)
        _execute(sql)
