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

from stdm.ui.composer.composer_field_selector import BaseComposerFieldSelector


class ComposerQREditor(BaseComposerFieldSelector):
    def __init__(self, *args, **kwargs):
        # Add label argument and set it as None to conform to parent class
        args = (args[0], None)
        super(ComposerQREditor, self).__init__(*args, **kwargs)

    def configuration(self):
        from stdm.composer.qr_code_configuration import QRCodeConfiguration

        # Assert field name has been selected
        if not self.fieldName():
            raise Exception(
                'Data field for QR code item cannot be empty.'
            )

        qrc_config = QRCodeConfiguration()
        qrc_config.data_source_field = self.fieldName()

        return qrc_config

    def set_configuration(self, configuration):
        # Load selected field name for generating QR codes
        self.selectFieldName(configuration.data_source_field)