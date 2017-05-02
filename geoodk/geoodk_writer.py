import os

from PyQt4.QtXml import QDomDocument, QDomElement
from PyQt4.QtCore import QFile, QIODevice, QTextStream
from PyQt4.QtGui import QApplication, QMessageBox

from stdm.data.configfile_paths import FilePaths


class GeoodkWriter():
    """
    """

    def __init__(self, iface):
        """
        It reads current
        :return:
        :rtype:
        """
        self.iface = iface
        self.file_handler = FilePaths()
        self.doc = QDomDocument()
        self.xform_file = None

    def _create_xform(self, file_name):
        """
        Method to create configuration file
        :param file_name:
        :return:
        """
        self.xform_file = QFile(os.path.join(self.file_handler.localPath(),
                                             file_name))

        if not self.xform_file.open(QIODevice.ReadWrite | QIODevice.Truncate |
                                             QIODevice.Text):
            title = QApplication.translate(
                'ConfigurationFileUpdater',
                'Configuration Upgrade Error'
            )
            message = QApplication.translate(
                'ConfigurationFileUpdater',
                'Cannot write file {0}: \n {2}'.format(
                    self.xform_file.fileName(),
                    self.xform_file.errorString()
                )
            )

            QMessageBox.warning(
                self.iface.mainWindow(), title, message
            )
        return

    def _create_model(self, entity, columns):
        """
        Method to create configuration file
        :param:
        :return:
        """

        model = self.doc.createElement("model")

        instance = self.doc.createElement("instance")

        instance_id = self.doc.createElement(entity)
        instance_id.setAttribute("id", entity)

        for column in columns:

            instance_id.appendChild(self.doc.createElement(column))

            bind = self.doc.createElement("bind")
            bind.setAttribute("nodeset", column)
            model.appendChild(bind)

        instance.appendChild(instance_id)
        model.appendChild(instance)

        return model

    def _create_xform_template(self, configuration):
        """
        Method to create configuration file
        :param:
        :return:
        """

        # Create xform file
        self._create_xform("xform.xml")

        # Create root
        self.doc.appendChild(
            self.doc.createProcessingInstruction("xml", "version=\"1.0\" "
                                                        "encoding=\"utf-8\""))
        root = self.doc.createElement("h:html")
        root.setAttribute("xmlns", "http://www.w3.org/2002/xforms")
        root.setAttribute("xmlns:ev",
                                  "http://www.w3.org/2001/xml-events")
        root.setAttribute("xmlns:h", "http://www.w3.org/1999/xhtml")
        root.setAttribute("xmlns:jr", "http://openrosa.org/javarosa")
        root.setAttribute("xmlns:orx", "http://openrosa.org/xforms")
        root.setAttribute("xmlns:xsd",
                                  "http://www.w3.org/2001/XMLSchema")

        # Add head
        head = self.doc.createElement("h:head")

        # Add title
        title = self.doc.createElement("h:title")

        for entity, columns in configuration.iteritems():

            title_text = self.doc.createTextNode(entity)
            title.appendChild(title_text)

            head.appendChild(title)
            model = self._create_model(entity, columns)

            head.appendChild(model)
            root.appendChild(head)

        self.doc.appendChild(root)

        stream = QTextStream(self.xform_file)
        stream << self.doc.toString()
        self.xform_file.close()
        self.doc.clear()