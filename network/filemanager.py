"""
/***************************************************************************
Name                 : Source Document File Manager
Description          : Manages the copying of source documents to/from a 
                       shared folder in a network.
Date                 : 7/August/2013 
copyright            : (C) 2014 by UN-Habitat and implementing partners.
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
from uuid import uuid4

from PyQt4.QtCore import (
    QObject,
    QThread,
    SIGNAL,
    pyqtSignal,
    QFile,
    pyqtSlot,
    QDir
)

from qgis.core import *

from stdm.utils import guess_extension

class NetworkFileManager(QObject):
    """
    Provides methods for managing the upload and download of source
    documents from a network repository.
    """
    def __init__(self, network_repository, parent=None):
        QObject.__init__(self, parent)
        self.network_path = network_repository
        self.file_id = None
        self.source_path = None
        self.destination_path = None
        self._document_type = ""
        
    def upload_document(self, doc_type, file_info):
        """
        Upload document in central repository
        """
        self._document_type = doc_type

        self.file_id = self.generate_file_id()
        self.source_path = file_info.filePath()

        root_dir = QDir(self.network_path)
        if not root_dir.exists(self._document_type):
            res = root_dir.mkdir(self._document_type)
            if res:
                root_doc_type_path = self.network_path + "/" + self._document_type
            else:
                root_doc_type_path = self.network_path
        else:
            root_doc_type_path = self.network_path + "/" + self._document_type

        self.destination_path = root_doc_type_path + "/" + self.file_id + "."  + \
                               file_info.completeSuffix()

        src_file = open(self.source_path,'rb')
        destination_file = open(self.destination_path,'wb')
        
        totalRead = 0
        
        while True:
            inbytes = src_file.read(4096)
            if not inbytes:
                break   
            destination_file.write(inbytes)
            total_read += len(inbytes)
            #Raise signal on each block written
            self.emit(SIGNAL("blockWritten(int)"), total_read)
            
        self.emit(SIGNAL("completed(QString)"), self.file_id)
            
        src_file.close()
        destination_file.close()
        
        return self.file_id
            
    def download_document(self, document_id):
        """
        Get the document from the central repository using its unique identifier.
        """
        pass

    def document_type(self):
        """
        Document type
        """
        return self._document_type

    def set_document_type(self, doc_type):
        """
        Specify the document type.
        """
        self._document_type = doc_type
    
    def delete_document(self, doc_model=None):
        """
        Delete the source document from the central repository.
        """
        if not doc_model is None:
            #Build the path from the model variable values.
            filename, file_ext = guess_extension(doc_model.file_name)
        
            #Qt always expects the file separator be be "/" regardless of platform.
            abs_path = self.network_path + "/" + "%d"%(doc_model.doc_type) + "/" +\
                      doc_model.doc_identifier + file_ext
            
            return QFile.remove(abs_path)
        
        else:
            return QFile.remove(self.destination_path)
    
    def generate_file_id(self):
        """
        Generates a unique file identifier that will be used to copy to the 
        """
        return str(uuid4())
        
class DocumentTransferWorker(QObject):
    """
    Worker thread for copying source documents to central repository.
    """
    block_write = pyqtSignal("int")
    complete = pyqtSignal("QString")
    
    def __init__(self, file_manager, file_info, document_type = "",
                 parent = None):
        QObject.__init__(self, parent)
        self._file_manager = file_manager
        self._file_info = file_info
        self._doc_type = document_type
    
    @pyqtSlot()    
    def transfer(self):
        """
        Initiate document transfer
        """
        self.connect(self._file_manager, SIGNAL("blockWritten(int)"),self.onBlockWritten)
        self.connect(self._file_manager, SIGNAL("completed(QString)"),self.onWriteComplete)
        self._file_manager.upload_document(self._doc_type, self._file_info)
        
    def onBlockWritten(self, size):
        """
        Propagate event.
        """
        self.blockWrite.emit(size)
        
    def onWriteComplete(self):
        """
        Propagate event.
        """
        self.complete.emit(self._file_manager.file_id)
        
