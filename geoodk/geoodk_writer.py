import os

from PyQt4.QtXml import (
    QDomDocument,
    QDomNode,
    QDomElement,
    QDomDocumentFragment,
    QXmlNamespaceSupport
)
from PyQt4.QtCore import QFile, QIODevice, QTextStream, QDate, QFileInfo
from PyQt4.QtGui import QApplication, QMessageBox

from stdm.data.configfile_paths import FilePaths
from xform_model import EntityFormatter
from stdm.geoodk import (
    GeoODKReader
)
from stdm.data.configuration.columns import BooleanColumn

DOCSUFFIX = 'h'
DOCEXTENSION = '.xml'
XFOFMDEFAULTS = ['start', 'end', 'deviceid', 'today']
BINDPARAMS = "jr:preloadParams"
CUSTOMBINDPARAMS = "jr:preload"


class XFORMDocument:
    """
    class to generate an Xml file that is needed for data collection
    using mobile device. The class creates the file and QDOM sections
    for holding data once the file is called
    """
    def __init__(self, fname):
        """
        Initalize the class so that we have a new file
        everytime document generation method is called
        """
        self.dt_text = QDate()
        self.file_handler = FilePaths()
        self.doc = QDomDocument()
        self.form = None
        self.fname = fname

    def form_name(self):
        """
        Format the name for a new file to be created. We need to ensure it is
        .xml file.
        :return: 
        """
        if len(self.fname.split(".")) > 1:
            return self.fname
        else:
            return self.fname+"{}".format(DOCEXTENSION)

    def set_form_name(self, local_name):
        """
        Allow the user to update the name of the file. This method
        will be called to return a new file with the local_name given
        :param local_name: string
        :return: QFile
        """
        self.fname = local_name+"{}".format(DOCEXTENSION)
        self.form.setFileName(self.fname)
        self.create_form()

        return self.fname

    def create_form(self):
        """
        Create an XML file that will be our XFORM Document for reading and writing
        We want a new file when everytime we are creating XForm
        type: file
        :return: file
        """
        self.form = QFile(os.path.join(self.file_handler.localPath(),
                                             self.form_name()))
        if not QFileInfo(self.form).suffix() == DOCEXTENSION:
            self.form_name()

        if not self.form.open(QIODevice.ReadWrite | QIODevice.Truncate |
                                            QIODevice.Text):
            return self.form.OpenError

    def create_node(self, name):
        """
        Create a XML element node
        :param name:
        :return:
        """
        return self.doc.createElement(name)


    def create_text_node(self, text):
        """
        Create an XML text node
        :param text:
        :return:
        """
        return self.doc.createTextNode(text)

    def create_node_attribute(self, node, key, value):
        """
        Create an attribute and attach it to the node
        :param node:
        :return:
        """
        return node.setAttribute(key, value)

    def xform_document(self):
        """

        :return:
        """
        return self.doc

    def write_to_form(self):
        """
        Write data to xml file from the base calling class to an output file created earlier
        :return: 
        """
        if isinstance(self.form, QFile):
            stream = QTextStream(self.form)
            stream << self.doc.toString()
            stream.flush()
            self.form.close()
            self.doc.clear()
        else:
            return None

    def update_form_data(self):
        """
        Update the xml file with changes that the user has made.
        Particular section of the document will be deleted or added
        :return: 
        """
        pass



class GeoodkWriter(EntityFormatter, XFORMDocument):
    """
    """

    def __init__(self, entities):
        """
        It reads current
        :return:
        :rtype:
        """
        self.entities = entities
        self.entity_read = None
        self.profile_entity = None
        self.prep_document_generators()


    def initialize_entity_reader(self, entity):
        """

        :return:
        """
        self.entity_read = GeoODKReader(entity)
        return self.entity_read

    def prep_document_generators(self):
        """
        Initialiaze base classes
        :return:
        """
        self.initialize_entity_reader(self.initialize_entity_reader(self.entities[0]))
        self.profile_entity = self.entity_read.profile_name()
        XFORMDocument.__init__(self, self.profile_entity)
        EntityFormatter.__init__(self, self.profile_entity)

        self.create_form()

    def _doc_meta_instance(self):
        """
        Create a meta section that will hold the key details of the form
        :return:
        """
        meta_node = self.create_node("meta")
        meta_id = self.create_node("instanceID")
        meta_node.appendChild(meta_id)
        return meta_node

    def create_xform_root_node(self):
        """
        Method to read and check the header node in the Xform document
        :return: Dom element
        """
        self.xform_document().appendChild(
                self.xform_document().createProcessingInstruction("xml", "version=\"1.0\" "))
        root = self.create_node("h:html")
        root.setPrefix(DOCSUFFIX)
        root.setAttribute("xmlns", "http://www.w3.org/2002/xforms")
        root.setAttribute("xmlns:ev",
                           "http://www.w3.org/2001/xml-events")
        root.setAttribute("xmlns:h", "http://www.w3.org/1999/xhtml")

        root.setAttribute("xmlns:orx", "http://openrosa.org/xforms")
        root.setAttribute("xmlns:xsd",
                           "http://www.w3.org/2001/XMLSchema")
        root.setAttribute("xmlns:jr", "http://openrosa.org/javarosa")
        return root

    def header_fragment_data(self):
        """
        Create and add data to the header node in Xform document
        :return:
        """
        doc_header = self.create_node("h:head")
        doc_header.setPrefix(DOCSUFFIX)
        doc_header.appendChild(self._header_title())
        doc_header.appendChild(self._header_model())
        return doc_header

    def _header_title(self):
        """
        Create header title in the document that is required by GeoODK
        :return:
        """
        title = self.create_node("h:title")
        title_text = self.create_text_node(self.entity_read.profile_name())
        title.appendChild(title_text)
        return title

    def _header_model(self):
        """
        Create a header model that GeoODK writer requires to create form
        :return:
        """
        doc_model = self.create_node("model")
        doc_model.appendChild(self._create_model_props())
        self.create_header_intro(doc_model)
        self.create_form_identifier_field(doc_model)
        self.bind_default_parameters(doc_model)
        self.create_model_bind_attributes(doc_model)
        doc_model.appendChild(self.model_unique_id_generator())
        return doc_model

    def intro_node(self):
        """
        Create header introduction label
        :return:
        """
        return self.create_node("intro")

    def parent_child_code_identifier(self):
        """
        Create a node that will hold a field for grouping entities
        User will input this code to enable idetification of related entities
        :return:
        """
        return self.create_node('identity')

    def create_header_intro(self, parent_node):
        """
        Create an introduction text available to user indicating which profile is on
        :return:
        """
        intro_node = self.create_node("bind")
        intro_node.setAttribute("readonly", "true()")
        intro_node.setAttribute("nodeset", self.set_model_xpath("intro"))
        intro_node.setAttribute("type", "string")
        parent_node.appendChild(intro_node)
        return intro_node

    def create_form_identifier_field(self, parent_node):
        """
        Create an introduction text available to user indicating which profile is on
        :return:
        """
        identifier_node = self.create_node("bind")
        #identifier_node.setAttribute("readonly", "true()")
        identifier_node.setAttribute("nodeset", self.set_model_xpath("identity"))
        identifier_node.setAttribute("type", "string")
        parent_node.appendChild(identifier_node)
        return identifier_node

    def _create_model_props(self):
        """
        Method to create configuration file
        :param:
        :return:
        """
        instance = self.create_node("instance")

        return self.on_instance_id_set_columns(instance)

    def on_instance_id_set_columns(self, instance):
        """
        Create an instance that will hold entity columns in Xform list
        :param instance:
        :return:
        """
        instance_id = self.create_node(self.profile_entity)
        instance_id.setAttribute("id", self.profile_entity)
        """ add entity data into the instance node as form fields
        language translation aspect of the instance child 
        has not been considered
        """
        intro = self.intro_node()
        identity = self.parent_child_code_identifier()
        instance_id.appendChild(intro)
        instance_id.appendChild(identity)
        if isinstance(self.entities, list):
            for entity in self.entities:
                self.initialize_entity_reader(entity)
                entity_values = self.entity_read.read_attributes()
                field_group = self.create_node(self.entity_read.default_entity())
                for key_field in entity_values.keys():
                    col_node = self.create_node(key_field)
                    field_group.appendChild(col_node)
                instance_id.appendChild(field_group)
                instance.appendChild(instance_id)
            instance_id.appendChild(self._doc_meta_instance())
            return instance

    def create_model_bind_attributes(self, base_node):
        """
        We need to iterate through each entity and bind the columns
        to xform format. The order does not matter
        :return:
        """
        if isinstance(self.entities, list):
            for entity in self.entities:
                self.initialize_entity_reader(entity)
                entity_values = self.entity_read.read_attributes()
                self.bind_model_attributes(base_node, entity_values)

    def bind_model_attributes(self, base_node, entity_values):
        """
        Method to create bind section of the form.
        Each attribute is bound to XForm property
        Creates XPath link for the attribute field
        Format the attribute data type to the XForm type
        :return: 
        """
        if hasattr(entity_values, "id"):
            entity_values.pop("id")
        for key, val in entity_values.iteritems():
            bind_node = self.create_node("bind")
            bind_node.setAttribute("nodeset",
                    self.set_model_xpath(key, self.entity_read.default_entity()))
            if self.entity_read.col_is_mandatory(key):
                bind_node.setAttribute("required", "true()")
            bind_node.setAttribute("type", self.set_model_data_type(val))

            base_node.appendChild(bind_node)
        return base_node

    def special_data_constraint(self, var):
        """
        Get data type like geometry and format to the type
        required
        :return:
        """
        #if var =='GEOMETRY':
        raise NotImplementedError


    def model_unique_id_generator(self):
        """
        Create static fields that  needed by XForm to hold instance GUUID
        :return:
        """
        bind_node = self.create_node("bind")
        bind_node.setAttribute("calculate", self.model_unique_uuid())
        bind_node.setAttribute("nodeset", self.set_model_xpath("meta/instanceID"))
        bind_node.setAttribute("readonly", "True")
        bind_node.setAttribute("type", "string")
        return bind_node

    def bind_default_parameters(self,parent_node):
        """
        Ensure that the default parameters fo Xform are included
        :return:
        """
        cast_param = ""
        for item_val in XFOFMDEFAULTS:
            bind_node = self.create_node("bind")
            if item_val == "deviceid":
                cast_param = "property"
            else:
                cast_param ="timestamp"
            bind_node.setAttribute(CUSTOMBINDPARAMS,cast_param)
            bind_node.setAttribute(BINDPARAMS, item_val)
            bind_node.setAttribute("nodeset", self.set_model_xpath(item_val))
            bind_node.setAttribute("type", self.xform_custom_params_types(item_val))
            parent_node.appendChild(bind_node)
        return parent_node

    def _body_section(self):
        """
        Method to read and check the body node in the Xform document is created
        :return: Dom element
        """
        body_section_node = self.create_node("h:body")
        #body_section_node.appendChild(self.create_nested_entity_data
        self.create_form_identifier(body_section_node)
        self.create_nested_entity_data(body_section_node)
        return body_section_node

    def create_form_identifier(self, parent):
        """
        Create a field for form Identifier for related field
        This will help in determining which parents entity and child entities
        are related.
        The user will input a unique code to identified relationship
        :return:
        """
        identifier_node = self.create_node("input")
        identifier_node.setAttribute("ref", self.set_model_xpath('identity'))

        group_label = self.create_node("label")
        label_txt = self.create_text_node('Enter Group Identifier')
        group_label.appendChild(label_txt)
        identifier_node.appendChild(group_label)
        parent.appendChild(identifier_node)


    def create_nested_entity_data(self, parent_node):
        """
        Format the groups to hold only one entity information
        :return:
        """
        if isinstance(self.entities, list):
            for entity in self.entities:
                self.initialize_entity_reader(entity)
                self.entity_read.get_user_selected_entity()
                entity_values = self.entity_read.read_attributes()
                group_node = self.body_section_categories(
                    self.entity_read.default_entity())
                self._body_section_data(entity_values,group_node)
                parent_node.appendChild(group_node)
            return parent_node

    def body_section_categories(self, entity):
        """
        Create groups that will contain each entity information
        :param item:
        :return:
        """
        cate_name = self.model_category_group(self.profile_entity,
                                              entity)
        group_node = self.create_node("group")
        group_node.setAttribute("appearance", "field-list")
        group_node.setAttribute("ref",cate_name)
        group_label = self.create_node("label")
        # label_txt = self.create_text_node(
        #     self.profile_entity + ": "+entity.replace("_", " ").title())
        label_txt = self.create_text_node(
            self.profile_entity + ": " + self.entity_read.user_entity_name())
        group_label.appendChild(label_txt)
        group_node.appendChild(group_label)
        return group_node

    def _body_section_data(self,entity_values, parent_node):
        """
        Add entity attribute to the body section as labels to the Xform file
        Create label fields to the input fields
        :return:
        """
        parent_path = self.profile_entity +"/"+ self.entity_read.default_entity()
        for key in entity_values.keys():
            if self.entity_read.on_column_info(key):
                self.format_lookup_data(key, parent_node)
            else:
                body_node = self.create_node("input")
                label_node = self.create_node("label")
                body_node.setAttribute("ref",self.model_category_group(parent_path, key))
                #label = "jr:itext('{0}:label')".format(self.set_model_xpath(key))
                label_txt= self.create_text_node(key.replace("_", " ").title())
                #label_node.setAttribute("ref", label)
                label_node.appendChild(label_txt)
                body_node.appendChild(label_node)
                parent_node.appendChild(body_node)

        return parent_node

    def format_lookup_data(self, col, parent_node):
        """
        Loop through the columns and if the column is a lookup
        Format it to the right format in Xform
        :param parent_node: the group holding the children
        :return:
        """
        self.entity_read.read_attributes()
        child_node = self.lookup_formatter(
            self.entity_read.default_entity(),col)
        parent_node.appendChild(child_node)

    def lookup_formatter(self, entity, col):
        """
        Format lookup to the Xform type
        :param lookup: entity name
        :param col: Lookup column
        :return:
        """
        self.entity_read.column_lookup_mapping()
        select_opt = "select1"
        if self.entity_read.column_info_multiselect(col):
            select_opt = "select"
        else:
            select_opt = select_opt
        lk_node = self.create_node(select_opt)
        lk_node.setAttribute("ref", self.set_model_xpath(col, entity))
        lk_node_label = self.create_node("label")
        lk_node_label_txt = self.create_text_node(
            self.entity_read.default_entity() + " " +
            col.replace("_"," ").title().replace("Id", ""))
        lk_node_label.appendChild(lk_node_label_txt)
        lk_node.appendChild(lk_node_label)

        # create lookup element on the form
        self.entity_read.get_user_selected_entity()
        col_obj = self.entity_read.entity_object().columns[col]

        lk_name_values = None
        if isinstance(col_obj, BooleanColumn):
            #Lookup values for yes no have been hardcoded
            lk_name_values = self.yes_no_list()
        else:
            #Read lookup from configuration
            lk_name_values = self.entity_read.format_lookup_items(col)
        if lk_name_values:
            for key, val in lk_name_values.iteritems():

                lk_item = self.create_node("item")
                lk_item_label = self.create_node("label")
                lk_item_label_txt = self.create_text_node(key)
                lk_item_label_txt_val = self.create_node("value")
                if val == "":
                    val = key
                lk_item_label_txt_val_txt = self.create_text_node(val)

                lk_item_label.appendChild(lk_item_label_txt)
                lk_item_label_txt_val.appendChild(lk_item_label_txt_val_txt)

                lk_item.appendChild(lk_item_label)
                lk_item.appendChild(lk_item_label_txt_val)
                lk_node.appendChild(lk_item)
        return lk_node

    def write_data_to_xform(self):
        """
        Method to create configuration file
        :param:
        :return:
        """
        # get all the document node and write the data to file
        root_node = self.create_xform_root_node()
        root_node.appendChild(self.header_fragment_data())
        root_node.appendChild(self._body_section())
        self.doc.appendChild(root_node)
        self.write_to_form()
