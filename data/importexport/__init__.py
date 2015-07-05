"""
STDM Import/Export module
"""
__author__ = 'John Gitau'
__license__ = 'GNU Lesser General Public License (LGPL)'
__url__ = 'http://www.unhabitat.org'

from stdm.settings import QGISRegistryConfig
from .exceptions import TranslatorException
from .reader import OGRReader
from .writer import OGRWriter
from .value_translators import (
    MultipleEnumerationTranslator,
    SourceValueTranslator,
    ValueTranslatorManager,
    RelatedTableTranslator
)

_UIGroup = "UI"
_lastVectorDirKey = "lastVectorFileFilterDir"

def vectorFileDir():
    """
    Returns the directory of the last vector file accessed by QGIS.
    """
    qgisReg = QGISRegistryConfig(_UIGroup)
    regValues = qgisReg.read([_lastVectorDirKey])
    
    if len(regValues) == 0:
        return ""
    else:
        return regValues[_lastVectorDirKey]
    
def setVectorFileDir(dir):
    """
    Update the last vector file directory.
    """
    qgisReg = QGISRegistryConfig(_UIGroup)
    qgisReg.write({_lastVectorDirKey:dir})

    
    