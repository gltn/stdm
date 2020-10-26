"""
/***************************************************************************
Name                 : Control Dirty Tracker package
Description          : Classes for tracking the dirty state of forms. If the
                       value of a control has changed from the previous 'clean' value,
                       then the form is considered dirty.
Date                 : 23/December/2013
copyright            : (C) 2013 by John Gitau
email                : gkahiu@gmail.com
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
from stdm.ui.helpers.valuehandlers import ControlValueHandler
from stdm.utils.util import getIndex


class ControlReaderMapper(object):
    '''
    Key-value mapper for control and their corresponding value readers.
    The reader must be a subclass of ControlValueReader class.
    '''

    def __init__(self, control, reader):
        self._control = control
        self._reader = reader
        self._reader.setControl(control)

    def control(self):
        '''
        Returns the control.
        '''
        return self._control

    def reader(self):
        '''
        Returns the reader for the specified control.
        '''
        return self._reader


class ControlDirtyTracker(object):
    '''
    Tracks a control's value based on its last saved state. It compares a
    control's current value to its remembered clean value. If the two values
    are different, then the control is considered "dirty" and so is the form.
    '''

    def __init__(self, controlReaderMapper):
        self._ctlRdMapper = controlReaderMapper
        self._cleanValue = None

        # If control is supported then set can track to True
        if ControlDirtyTracker.isControlTypeSupported(self._ctlRdMapper.control())[0]:
            self._cleanValue = self.controlCurrentValue()

    @staticmethod
    def isControlTypeSupported(ctl):
        '''
        Returns whether or not the control type of the given control is supported
        by this class. If the control type is supported then the corresponding
        value handler is returned.
        This is based on whether there exists a registered value handler class
        for the specified control.
        '''
        # Define default list of supported control names
        supportedControls = ControlValueHandler.handlers.keys()
        ctlName = str(ctl.metaObject().className())

        handler = None

        typeIndex = getIndex(supportedControls, ctlName)

        if typeIndex == -1:
            return False, handler
        else:
            handler = ControlValueHandler.handlers[ctlName]
            return True, handler

    def control(self):
        '''
        Returns the control currently being referenced by the tracker
        '''
        return self._ctlRdMapper.control()

    def controlCurrentValue(self):
        '''
        Returns the current control value based on the type of control.
        '''
        # Validate
        if self._ctlRdMapper.reader().isControlTypeValid():
            return self._ctlRdMapper.reader().value()

    def setValueAsClean(self):
        '''
        Establish the current control value as 'clean'.
        '''
        self._cleanValue = self.controlCurrentValue()

    def isDirty(self):
        '''
        Determine if the current control value is considered 'dirty' i.e.
        if the current control value is different than the one remembered
        as clean.
        Custom data types have to implement __ne__ special method of
        the Python 'object' class as the '!=' operator will be used to
        compare the values.
        '''
        return self._cleanValue != self.controlCurrentValue()


class ControlDirtyTrackerCollection(object):
    '''
    Enables us to track multiple controls in a widget or dialog.
    '''

    def __init__(self):
        self._ctlTrackerColl = []

    def addControl(self, control, reader=None):
        '''
        Register a control and its corresponding reader for monitoring its dirty state.
        '''
        # Try to search through registered value handlers
        if reader == None:
            supported, handler = ControlDirtyTracker.isControlTypeSupported(control)
            # Do not add to the collection if a matching reader does not exist
            if not supported:
                return
            reader = handler()

        ctlRdMapper = ControlReaderMapper(control, reader)
        self.RegisterControlReaderMappersForMonitor(ctlRdMapper)

    def addControlReaderMapper(self, ctlrdmapper):
        '''
        Register a ControlReaderMapper object.
        '''
        self.RegisterControlReaderMappersForMonitor(ctlrdmapper)

    def RegisterControlReaderMappersForMonitor(self, ctlrdmapper):
        '''
        Validate if the control is supported and if true, add it to the collection.
        '''
        ctlTracker = ControlDirtyTracker(ctlrdmapper)
        self._ctlTrackerColl.append(ctlTracker)

    def dirtyControls(self):
        '''
        Loops through all registered controls and returns a list of those that are dirty.
        '''
        dirtyList = []

        for ct in self._ctlTrackerColl:
            if ct.isDirty():
                dirtyList.append(ct.control())

        return dirtyList

    def isDirty(self):
        '''
        Asserts whether one or more of the tracked controls are dirty.
        '''
        return len(self.dirtyControls()) > 0

    def markAllControlsAsClean(self):
        '''
        Mark all the tracked controls as clean.
        '''
        for ct in self._ctlTrackerColl:
            ct.setValueAsClean()
