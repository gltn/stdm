_UIGroup = "UI"
_lastVectorDirKey = "lastVectorFileFilterDir"

def vectorFileDir():
    """
    Returns the directory of the last vector file accessed by QGIS.
    """
    from stdm.settings.registryconfig import QGISRegistryConfig

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
    from stdm.settings.registryconfig import QGISRegistryConfig

    qgisReg = QGISRegistryConfig(_UIGroup)
    qgisReg.write({_lastVectorDirKey:dir})


