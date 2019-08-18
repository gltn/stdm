"""
/***************************************************************************
Name                 : Scheme Model
Description          : Model for handling scheme table data in
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
Date                 : 11/August/2019
copyright            : (C) 2019
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy import exc


class SchemeModel(QAbstractTableModel):
    """
    Handles data for Scheme Establishment and First, Second
    and Third Examination FLTS modules
    """

    def __init__(self, entity_model):
        super(SchemeModel, self).__init__()
        self._entity_model = entity_model
        self.results = None

    def load(self):
        exception = None
        try:
            entity_object = self._entity_model()
            self.results = entity_object.queryObject().order_by(self._entity_model.id).all()
            print(0)
        except exc.SQLAlchemyError as sql_error:
            exception = sql_error
        except Exception as e:
            exception = e
        finally:
            if exception:
                raise exception

