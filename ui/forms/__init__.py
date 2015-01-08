"""
/***************************************************************************
Name                 : Generic application for generating forms
Description          : User forms
Date                 : 30/June/2014 
copyright            : (C) 2014 by Solomon Njogu
email                : njoroge.solomon.com
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
from .attribute_datatype import AttributePropretyType
from .mapper_dialog import CustomFormDialog
from .widgets import (
                    DateWidget,
                    CharacterWidget,
                    IntegerWidget,
                    DoubleWidget,
                    ChoiceListWidget,
                    widgetCollection
)
from .property_mapper import TypePropertyMapper

