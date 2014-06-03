"""
/***************************************************************************
Name                 : Source Document File Manager
Description          : Manages the copying of source documents to/from a 
                       shared folder in a network.
Date                 : 7/August/2013 
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
from uuid import uuid4

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

from stdm.utils import *

class NetworkFileManager(QObject):
    '''
    Provides methods for managing the upload and download of source
    documents from a network repository.
    '''
    def __init__(self,networkrepository,parent = None):
        '''
        Set the location of the central repository in the constructor.
        '''
        QObject.__init__(self,parent)
        self.networkPath = networkrepository
        self.fileID = None
        self.sourcePath = None
        self.destinationPath = None
        
    def uploadDocument(self,fileinfo):
        '''
        Upload document in central repository
        '''
        self.fileID = self.generateFileID()
        self.sourcePath = str(fileinfo.filePath())
        srcFile = open(self.sourcePath,'rb')
        self.destinationPath = str(self.networkPath + "/" + self.fileID + "."  + fileinfo.completeSuffix())
        destinationFile = open(self.destinationPath,'wb')
        
        #srcLen = self.sourceFile.bytesAvailable()
        totalRead = 0
        
        while True:
            inbytes = srcFile.read(4096)
            if not inbytes:
                break   
            destinationFile.write(inbytes)
            totalRead += len(inbytes)
            #Raise signal on each block written
            self.emit(SIGNAL("blockWritten(int)"),totalRead)
            
        self.emit(SIGNAL("completed(QString)"),self.fileID)
            
        srcFile.close()
        destinationFile.close()
        
        return self.fileID
            
    def downloadDocument(self,documentid):
        '''
        Get the document from the central repository using its unique identifier.
        '''
        pass
    
    def deleteDocument(self,docmodel = None):
        '''
        Delete the source document from the central repository.
        '''
        if docmodel:
            #Build the path from the model variable values.
            fileName,fileExt = guess_extension(docmodel.FileName)
        
            #Qt always expects the file separator be be "/" regardless of platform.
            absPath = self.networkPath + "/" + docmodel.DocumentID + fileExt
            
            return True #QFile.remove(absPath)
        
        else:
            return True #QFile.remove(self.destinationPath)
    
    def generateFileID(self):
        '''
        Generates a unique file identifier that will be used to copy to the 
        '''
        return str(uuid4())
        
class DocumentTransferWorker(QObject):
    '''
    Worker thread for copying source documents to central repository.
    '''
    blockWrite = pyqtSignal("int")
    complete = pyqtSignal("QString")
    
    def __init__(self,filemanager,fileinfo,parent = None):
        QObject.__init__(self,parent)
        self.fileManager = filemanager
        self.fileinfo = fileinfo
    
    @pyqtSlot()    
    def transfer(self):
        '''
        Initiate document transfer
        '''   
        self.connect(self.fileManager, SIGNAL("blockWritten(int)"),self.onBlockWritten)
        self.connect(self.fileManager, SIGNAL("completed(QString)"),self.onWriteComplete)
        self.fileManager.uploadDocument(self.fileinfo)
        
    def onBlockWritten(self,size):
        '''
        Propagate event.
        '''
        self.blockWrite.emit(size)
        
    def onWriteComplete(self):
        '''
        Propagate event.
        '''
        self.complete.emit(self.fileManager.fileID)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        