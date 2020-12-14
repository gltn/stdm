"""
/***************************************************************************
Name                 : ComposerQRCodeEditor
Description          : Widget for specifying QR code properties in the
                       document designer.
Date                 : 17/March/2019
copyright            : (C) 2019 by UN-Habitat and implementing partners.
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

from qgis.core import QgsLayoutItem

from stdm.ui.composer.composer_field_selector import BaseComposerFieldSelector


class ComposerQREditor(BaseComposerFieldSelector):

    def __init__(self, item: QgsLayoutItem, parent=None):
        super().__init__(item, parent)
