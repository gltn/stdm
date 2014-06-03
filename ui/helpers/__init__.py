from .dirtytracker import ControlDirtyTracker,ControlDirtyTrackerCollection, \
ControlReaderMapper
from .valuehandlers import CheckBoxValueHandler,ControlValueHandler,LineEditValueHandler, \
ComboBoxValueHandler,TextEditValueHandler, DateEditValueHandler, SourceDocManagerValueHandler, \
ForeignKeyMapperValueHandler,SpinBoxValueHandler,DoubleSpinBoxValueHandler,CoordinatesWidgetValueHandler
from .datamanagemixin import SupportsManageMixin

def valueHandler(ctl):
    '''
    Factory that returns the corresponding value handler based on the control type.
    '''
    ctlName = str(ctl.metaObject().className())
    
    if ctlName in ControlValueHandler.handlers:
        return ControlValueHandler.handlers[ctlName]
    else:
        return None
    
