"""
/***************************************************************************
Name                 : Scheme Details View
Description          : Table view widget for viewing scheme holders and
                       supporting documents for workflow manager modules;
                       Scheme Establishment and First, Second and
                       Third Examination FLTS modules.
Date                 : 22/August/2019
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

from PyQt4.QtGui import *
from sqlalchemy import exc
from sqlalchemy.orm import joinedload
from stdm.ui.flts.workflow_manager.config import SchemeConfig
from stdm.ui.flts.workflow_manager.config import StyleSheet
from stdm.data.configuration import entity_model
from stdm.settings import current_profile
from stdm.ui.flts.workflow_manager.model import WorkflowManagerModel

pass

