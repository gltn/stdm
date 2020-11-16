"""
/***************************************************************************
Name                 : Document Generator class
Description          : Generates documents from user-defined templates.
Date                 : 21/May/2014
copyright            : (C) 2014 by John Gitau
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
import logging
import uuid
from datetime import date, datetime
from numbers import Number

from qgis.PyQt.QtCore import (
    QObject,
    QIODevice,
    QFile,
    QFileInfo,
    QDir
)
from qgis.PyQt.QtWidgets import (
    QApplication
)
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    QgsLayoutItemLabel,
    QgsLayoutItemMap,
    QgsLayoutItemPicture,
    QgsPrintLayout,
    QgsFeature,
    QgsGeometry,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.schema import (
    Table,
    MetaData
)

from stdm.composer.chart_configuration import ChartConfigurationCollection
from stdm.composer.composer_data_source import ComposerDataSource
from stdm.composer.composer_wrapper import load_table_layers
from stdm.composer.photo_configuration import PhotoConfigurationCollection
from stdm.composer.qr_code_configuration import QRCodeConfigurationCollection
from stdm.composer.spatial_fields_config import SpatialFieldsConfiguration
from stdm.composer.table_configuration import TableConfigurationCollection
from stdm.data.database import STDMDb
from stdm.data.pg_utils import (
    geometryType,
    pg_table_exists,
    vector_layer
)
from stdm.settings import (
    current_profile
)
from stdm.settings.registryconfig import RegistryConfig
from stdm.ui.forms.widgets import EntityValueFormatter
from stdm.ui.sourcedocument import (
    network_document_path
)
from stdm.utils.util import PLUGIN_DIR

LOGGER = logging.getLogger('stdm')


class DocumentGenerator(QObject):
    """
    Generates documents from user-defined templates.
    """

    #Output type enumerations
    Image = 0
    PDF = 1

    def __init__(self, iface, parent = None):
        QObject.__init__(self,parent)
        self._iface = iface
        self._map_renderer = self._iface.mapCanvas().mapRenderer()
        self._map_settings = self._iface.mapCanvas().mapSettings()
        self._dbSession = STDMDb.instance().session
        self._attr_value_formatters = {}

        self._current_profile = current_profile()
        if self._current_profile is None:
            raise Exception('Current data profile has not been set.')

        #For cleanup after document compositions have been created
        self._map_memory_layers = []
        self.map_registry = QgsProject.instance()
        self._table_mem_layers = []
        self._feature_ids = []

        self._link_field = ""

        self._base_photo_table = "supporting_document"

        #Value formatter for output files
        self._file_name_value_formatter = None

    def link_field(self):
        """
        :return: The field name in the data source that should also exist
        in the configuration for composer items that require to use this
        reference for additional queries. This should be the name of the
        field in the child table linked through a foreign key.
        :rtype: str
        """
        return self._link_field

    def set_link_field(self, field):
        """
        :param field: Name of the link field in the data source
        :type field: str
        """
        self._link_field = field

    def set_attr_value_formatters(self, formattermapping):
        """
        Dictionary of attribute mappings and corresponding functions for
        formatting the attribute value when naming an output file using
        attribute values.
        """
        self._attr_value_formatters = formattermapping

    def add_attr_value_formatter(self,attributeName,formatterFunc):
        """
        Add a new attribute value formatter configuration to the collection.
        """
        self._attr_value_formatters[attributeName] = formatterFunc

    def clear_attr_value_formatters(self):
        """
        Removes all value formatters.
        """
        self._attr_value_formatters = {}

    def attr_value_formatters(self):
        """
        Returns a dictionary of attribute value formatters used by the document generators.
        """
        return self._attr_value_formatters

    def data_source_exists(self, data_source):
        """
        :param data_source: Data source object containing table/view name and
        corresponding columns.
        :type data_source: ComposerDataSource
        :return: Checks if the table or view specified in the data source exists.
        :rtype: str
        """
        return pg_table_exists(data_source.name())

    def template_document(self, path):
        """
        Reads the document template file and returns the corresponding
        QDomDocument.
        :param path: Absolute path to template file.
        :type path: str
        :return: A tuple containing the template document and error message
        where applicable
        :rtype: tuple
        """
        if not path:
            return None, QApplication.translate("DocumentGenerator",
                                                "Empty path to document template")

        if not QFile.exists(path):
            return None, QApplication.translate("DocumentGenerator",
                                                "Path to document template "
                                                "does not exist")

        template_file = QFile(path)

        if not template_file.open(QIODevice.ReadOnly):
            return None, QApplication.translate("DocumentGenerator",
                                            "Cannot read template file")

        template_doc = QDomDocument()

        if template_doc.setContent(template_file):
            return template_doc, ""

        return None, QApplication.translate("DocumentGenerator",
                                            "Cannot read document template contents")

    def composer_data_source(self, template_document):
        """
        :param template_document: Document containing document composition
        information.
        :type template_document: QDomDocument
        :return: Returns the data source defined in the template document.
        :rtype: ComposerDataSource
        """
        composer_ds = ComposerDataSource.create(template_document)

        if not self.data_source_exists(composer_ds):
            msg = QApplication.translate("DocumentGenerator",
                                             "'{0}' data source does not exist in the database."
                                             "\nPlease contact your database "
                                             "administrator.".format(composer_ds.name()))

            return None, msg

        return composer_ds, ""

    def run(self, *args, **kwargs):
        """
        :param templatePath: The file path to the user-defined template.
        :param entityFieldName: The name of the column for the specified entity which
        must exist in the data source view or table.
        :param entityFieldValue: The value for filtering the records in the data source
        view or table.
        :param outputMode: Whether the output composition should be an image or PDF.
        :param filePath: The output file where the composition will be written to. Applies
        to single mode output generation.
        :param dataFields: List containing the field names whose values will be used to name the files.
        This is used in multiple mode configuration.
        :param fileExtension: The output file format. Used in multiple mode configuration.
        :param data_source: Name of the data source table or view whose
        row values will be used to name output files if the options has been
        specified by the user.
        """
        templatePath = args[0]
        entityFieldName = args[1]
        entityFieldValue = args[2]
        outputMode = args[3]
        filePath = kwargs.get("filePath", None)
        dataFields = kwargs.get("dataFields", [])
        fileExtension = kwargs.get("fileExtension", "")
        data_source = kwargs.get("data_source", "")

        templateFile = QFile(templatePath)

        if not templateFile.open(QIODevice.ReadOnly):
            return False, QApplication.translate("DocumentGenerator",
                                            "Cannot read template file.")

        templateDoc = QDomDocument()

        if templateDoc.setContent(templateFile):
            composerDS = ComposerDataSource.create(templateDoc)
            spatialFieldsConfig = SpatialFieldsConfiguration.create(templateDoc)
            composerDS.setSpatialFieldsConfig(spatialFieldsConfig)

            #Check if data source exists and return if it doesn't
            if not self.data_source_exists(composerDS):
                msg = QApplication.translate("DocumentGenerator",
                                             "'{0}' data source does not exist in the database."
                                             "\nPlease contact your database "
                                             "administrator.".format(composerDS.name()))
                return False, msg

            #Set file name value formatter
            self._file_name_value_formatter = EntityValueFormatter(
                name=data_source
            )

            #Register field names to be used for file naming
            self._file_name_value_formatter.register_columns(dataFields)

            #TODO: Need to automatically register custom configuration collections
            #Photo config collection
            ph_config_collection = PhotoConfigurationCollection.create(templateDoc)

            #Table configuration collection
            table_config_collection = TableConfigurationCollection.create(templateDoc)

            #Create chart configuration collection object
            chart_config_collection = ChartConfigurationCollection.create(templateDoc)

            # Create QR code configuration collection object
            qrc_config_collection = QRCodeConfigurationCollection.create(templateDoc)

            #Load the layers required by the table composer items
            self._table_mem_layers = load_table_layers(table_config_collection)

            entityFieldName = self.format_entity_field_name(composerDS.name(), data_source)

            #Execute query
            dsTable,records = self._exec_query(composerDS.name(), entityFieldName, entityFieldValue)

            if records is None or len(records) == 0:
                return False, QApplication.translate("DocumentGenerator",
                                                    "No matching records in the database")

            """
            Iterate through records where a single file output will be generated for each matching record.
            """

            for rec in records:
                composition = QgsPrintLayout(self._map_settings)
                composition.loadFromTemplate(templateDoc)
                ref_layer = None
                #Set value of composer items based on the corresponding db values
                for composerId in composerDS.dataFieldMappings().reverse:
                    #Use composer item id since the uuid is stripped off
                    composerItem = composition.getComposerItemById(composerId)
                    if not composerItem is None:
                        fieldName = composerDS.dataFieldName(composerId)
                        fieldValue = getattr(rec,fieldName)
                        self._composeritem_value_handler(composerItem, fieldValue)

                # Extract photo information
                self._extract_photo_info(composition, ph_config_collection, rec)

                # Set table item values based on configuration information
                self._set_table_data(composition, table_config_collection, rec)

                # Refresh non-custom map composer items
                self._refresh_composer_maps(composition,
                                            list(spatialFieldsConfig.spatialFieldsMapping().keys()))

                # Set use fixed scale to false i.e. relative zoom
                use_fixed_scale = False

                # Create memory layers for spatial features and add them to the map
                for mapId,spfmList in spatialFieldsConfig.spatialFieldsMapping().items():

                    map_item = composition.getComposerItemById(mapId)

                    if not map_item is None:
                        # Clear any previous map memory layer
                        # self.clear_temporary_map_layers()
                        for spfm in spfmList:
                            #Use the value of the label field to name the layer
                            lbl_field = spfm.labelField()
                            spatial_field = spfm.spatialField()

                            if not spatial_field:
                                continue

                            if lbl_field:
                                if hasattr(rec, spfm.labelField()):
                                    layerName = getattr(rec, spfm.labelField())
                                else:
                                    layerName = self._random_feature_layer_name(spatial_field)
                            else:
                                layerName = self._random_feature_layer_name(spatial_field)

                            #Extract the geometry using geoalchemy spatial capabilities
                            geom_value = getattr(rec, spatial_field)
                            if geom_value is None:
                                continue

                            geom_func = geom_value.ST_AsText()
                            geomWKT = self._dbSession.scalar(geom_func)

                            #Get geometry type
                            geom_type, srid = geometryType(composerDS.name(),
                                                          spatial_field)

                            #Create reference layer with feature
                            ref_layer = self._build_vector_layer(layerName, geom_type, srid)

                            if ref_layer is None or not ref_layer.isValid():
                                continue
                            # Add feature
                            bbox = self._add_feature_to_layer(ref_layer, geomWKT)

                            zoom_type = spfm.zoom_type
                            # Only scale the extents if zoom type is relative
                            if zoom_type == 'RELATIVE':
                                bbox.scale(spfm.zoomLevel())

                            #Workaround for zooming to single point extent
                            if ref_layer.wkbType() == QgsWkbTypes.Point:
                                canvas_extent = self._iface.mapCanvas().fullExtent()
                                cnt_pnt = bbox.center()
                                canvas_extent.scale(1.0/32, cnt_pnt)
                                bbox = canvas_extent

                            #Style layer based on the spatial field mapping symbol layer
                            symbol_layer = spfm.symbolLayer()
                            if not symbol_layer is None:
                                ref_layer.rendererV2().symbols()[0].changeSymbolLayer(0,spfm.symbolLayer())
                            '''
                            Add layer to map and ensure its always added at the top
                            '''
                            self.map_registry.addMapLayer(ref_layer)
                            self._iface.mapCanvas().setExtent(bbox)

                            # Set scale if type is FIXED
                            if zoom_type == 'FIXED':
                                self._iface.mapCanvas().zoomScale(spfm.zoomLevel())
                                use_fixed_scale = True

                            self._iface.mapCanvas().refresh()
                            # Add layer to map memory layer list
                            self._map_memory_layers.append(ref_layer.id())
                            self._hide_layer(ref_layer)
                        '''
                        Use root layer tree to get the correct ordering of layers
                        in the legend
                        '''
                        self._refresh_map_item(map_item, use_fixed_scale)

                # Extract chart information and generate chart
                self._generate_charts(composition, chart_config_collection, rec)

                # Extract QR code information in order to generate QR codes
                self._generate_qr_codes(composition, qrc_config_collection,rec)

                #Build output path and generate composition
                if not filePath is None and len(dataFields) == 0:
                    self._write_output(composition, outputMode, filePath)

                elif filePath is None and len(dataFields) > 0:
                    entityFieldName = 'id'
                    docFileName = self._build_file_name(data_source, entityFieldName,
                                                      entityFieldValue, dataFields, fileExtension)

                    # Replace unsupported characters in Windows file naming
                    docFileName = docFileName.replace('/', '_').replace \
                        ('\\', '_').replace(':', '_').strip('*?"<>|')


                    if not docFileName:
                        return (False, QApplication.translate("DocumentGenerator",
                                    "File name could not be generated from the data fields."))

                    outputDir = self._composer_output_path()
                    if outputDir is None:
                        return (False, QApplication.translate("DocumentGenerator",
                            "System could not read the location of the output directory in the registry."))

                    qDir = QDir()
                    if not qDir.exists(outputDir):
                        return (False, QApplication.translate("DocumentGenerator",
                                "Output directory does not exist"))

                    absDocPath = "{0}/{1}".format(outputDir, docFileName)
                    self._write_output(composition, outputMode, absDocPath)

            return True, "Success"

        return False, "Document composition could not be generated"

    def format_entity_field_name(self, composer_datasource, entity):
        if '_vw_' in composer_datasource:
            return composer_datasource+'.'+entity[entity.find('_')+1:]+'_id'
        else:
            return 'id'

    def _random_feature_layer_name(self, sp_field):
        return "{0}-{1}".format(sp_field, str(uuid.uuid4())[0:8])

    def _refresh_map_item(self, map_item, use__fixed_scale=False):
        """
        Updates the map item with the current extents and layer set in the
        map canvas.
        """
        mode = map_item.previewMode()
        if mode == QgsLayoutItemMap.Rectangle:
            tree_layers = QgsProject.instance().layerTreeRoot().findLayers()
            layer_ids = [lyt.layerId() for lyt in tree_layers]
            map_item.setLayerSet(layer_ids)
            map_item.zoomToExtent(self._iface.mapCanvas().extent())

            # If use_scale is True then set NewScale based on that of the
            # map renderer.
            if use__fixed_scale:
                map_item.setNewScale(self._iface.mapCanvas().scale())

    def _refresh_composer_maps(self, composition, ignore_ids):
        """
        Refreshes only those map composer items whose ids are not in the list
        of 'ignore_ids'.
        """
        c_maps = composition.composerMapItems()
        for c_map in c_maps:
            if not c_map.id() in ignore_ids:
                self._refresh_map_item(c_map)

    def clear_temporary_map_layers(self):
        """
        Clears all memory map layers that were
        used to create the composition.
        """
        self._clear_layers(self._map_memory_layers)

    def clear_temporary_table_layers(self):
        """
        Clears all table layers for attribute tables.
        """
        self._clear_layers(self._table_mem_layers)

    def clear_temporary_layers(self):
        """
        Clears all temporary layers, both spatial and table layers.
        """
        self.clear_temporary_map_layers()
        self.clear_temporary_table_layers()

    def _clear_layers(self, layers):
        if layers is None:
            return
        try:
            for lyr_id in layers:
                self.map_registry.removeMapLayer(lyr_id)
                layers.remove(lyr_id)

        except Exception as ex:
            LOGGER.debug(
                'Could not delete temporary designer layer. {}'.
                    format(ex)
            )

    def _hide_layer(self, layer):
        """
        Hides a layer from the canvas.
        :param layer: The layer to be hidden.
        :type layer: QgsVectorLayer
        :return: None
        :rtype: NoneType
        """
        self._iface.legendInterface().setLayerVisible(
            layer, False
        )

    def _build_vector_layer(self, layer_name, geom_type, srid):
        """
        Builds a memory vector layer based on the spatial field mapping properties.
        """
        vl_geom_config = "{0}?crs=epsg:{1:d}&field=name:string(20)&" \
                         "index=yes".format(geom_type, srid)

        ref_layer = QgsVectorLayer(vl_geom_config, str(layer_name), "memory")
        return ref_layer

    def _load_table_layers(self, config_collection):
        """
        In order to use attribute tables in the composition, the
        corresponding vector layers need to be added to the layer
        registry. This method creates vector layers from the linked tables
        in the configuration items. This is required prior to creating the
        composition from file.
        :param config_collection: Table configuration collection built from
        the template file.
        :type config_collection: TableConfigurationCollection
        """
        table_configs = list(config_collection.items()).values()

        v_layers = []

        for conf in table_configs:

            layer_name = conf.linked_table()

            v_layer = vector_layer(layer_name)

            if v_layer is None:
                return

            if not v_layer.isValid():
                return

            v_layers.append(v_layer)

            self._map_memory_layers.append(v_layer.id())

        self.map_registry.addMapLayers(v_layers, False)

    def _set_table_data(self, composition, config_collection, record):
        #TODO: Clean up code to adopt this design.
        """
        Set table data by applying appropriate filter using information
        from the config item and the record value.
        :param composition: Map composition.
        :type composition: QgsComposition
        :param config_collection: Table configuration collection specified in
        template file.
        :type config_collection: TableConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """
        table_configs = list(config_collection.items()).values()

        for conf in table_configs:
            table_handler = conf.create_handler(composition, self._exec_query)
            table_handler.set_data_source_record(record)

    def _generate_charts(self, composition, config_collection, record):
        """
        Extract chart information and use it to generate charts, which are
        exported as images then embedded in the composition as pictures.
        :param composition: Map composition
        :type composition: QgsComposition
        :param config_collection: Chart configuration collection specified
        in template file.
        :type config_collection: ChartConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """

        chart_configs = list(config_collection.items()).values()

        for cc in chart_configs:
            chart_handler = cc.create_handler(composition, self._exec_query)
            chart_handler.set_data_source_record(record)

    def _generate_qr_codes(self, composition, config_collection, record):
        """
        Extract QR code information and use it to generate QR codes, which are
        exported as images then embedded in the composition as pictures.
        :param composition: Map composition
        :type composition: QgsComposition
        :param config_collection: QR code configuration collection specified
        in template file.
        :type config_collection: QRCodeConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """

        qrc_configs = list(config_collection.items()).values()

        for qrc in qrc_configs:
            qrc_handler = qrc.create_handler(composition, self._exec_query)
            qrc_handler.set_data_source_record(record)

    def _extract_photo_info(self, composition, config_collection, record):
        """
        Extracts the photo information from the config using the record value
        and builds an absolute path for use by the picture composer item.
        :param composition: Map composition.
        :type composition: QgsComposition
        :param config_collection: Photo configuration collection specified in
        template file.
        :type config_collection: PhotoConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """
        ph_configs = list(config_collection.items()).values()

        for conf in ph_configs:
            photo_tb = conf.linked_table()
            referenced_column = conf.source_field()
            referencing_column = conf.linked_field()
            document_type = conf.document_type.replace(' ', '_').lower()
            document_type_id = int(conf.document_type_id)

            #Get name of base supporting documents table
            supporting_doc_base = self._current_profile.supporting_document.name

            #Get parent table of supporting document table
            s_doc_entities = self._current_profile.supporting_document_entities()
            photo_doc_entities = [de for de in s_doc_entities
                                   if de.name == photo_tb]

            if len(photo_doc_entities) == 0:
                continue

            photo_doc_entity = photo_doc_entities[0]
            document_parent_table = photo_doc_entity.parent_entity.name

            #Get id of base photo
            alchemy_table, results = self._exec_query(
                photo_tb,
                referencing_column,
                getattr(record, referenced_column, '')
            )

            #Filter results further based on document type
            results = [r for r in results
                       if r.document_type == document_type_id]

            '''
            There are no photos in the referenced table column hence insert no
            photo image
            '''
            if len(results) == 0:
                pic_item = composition.getComposerItemById(conf.item_id())

                if not pic_item is None:
                    no_photo_path = PLUGIN_DIR + "/images/icons/no_photo.png"

                    if QFile.exists(no_photo_path):
                        self._composeritem_value_handler(pic_item, no_photo_path)

                    continue

            for r in results:
                base_ph_table, doc_results = self._exec_query(
                    supporting_doc_base,
                    'id',
                    r.supporting_doc_id
                )

                for dr in doc_results:
                    self._build_photo_path(
                        composition,
                        conf.item_id(),
                        document_parent_table,
                        document_type,
                        dr.document_identifier,
                        dr.filename
                    )

                #TODO: Only interested in one photograph, should support more?
                break

    def _build_photo_path(
            self,
            composition,
            composer_id,
            document_parent_table,
            document_type,
            doc_id,
            doc_name
    ):
        pic_item = composition.getComposerItemById(composer_id)

        if pic_item is None:
            return

        extensions = doc_name.rsplit(".", 1)
        if len(extensions) < 2:
            return

        network_ph_path = network_document_path()
        if not network_ph_path:
            return

        img_extension = extensions[1]
        profile_name = self._current_profile.name.replace(' ', '_').lower()
        abs_path = '{0}/{1}/{2}/{3}/{4}.{5}'.format(
            network_ph_path,
            profile_name,
            document_parent_table,
            document_type,
            doc_id,
            img_extension
        )

        if QFile.exists(abs_path):
            self._composeritem_value_handler(pic_item, abs_path)

    def _add_feature_to_layer(self, vlayer, geom_wkb):
        """
        Create feature and add it to the vector layer.
        Return the extents of the geometry.
        """
        if not isinstance(vlayer, QgsVectorLayer):
            return
        dp = vlayer.dataProvider()

        feat = QgsFeature()
        g = QgsGeometry.fromWkt(geom_wkb)
        feat.setGeometry(g)

        dp.addFeatures([feat])
        self._feature_ids.append(feat.id())
        vlayer.updateExtents()

        return g.boundingBox()

    def _write_output(self,composition,outputMode,filePath):
        """
        Write composition to file based on the output type (PDF or IMAGE).
        """
        if outputMode == DocumentGenerator.Image:
            self._export_composition_as_image(composition,filePath)

        elif outputMode == DocumentGenerator.PDF:
            self._export_composition_as_pdf(composition,filePath)

    def _export_composition_as_image(self, composition, file_path):
        """
        Export the composition as a raster image.
        """
        num_pages = composition.numPages()

        for p in range(num_pages):
            img = composition.printPageAsRaster(p)

            if img.isNull():
                msg = QApplication.translate("DocumentGenerator",
                                        "Memory allocation error. Please try "
                                        "a lower resolution or a smaller paper size.")
                raise Exception(msg)

            if p == 0:
                state = img.save(file_path)

            else:
                fi = QFileInfo(file_path)
                file_path = "{0}/{1}_{2}.{3}".format(fi.absolutePath(),
                                                             fi.baseName(),
                    (p+1), fi.suffix())
                state = img.save(file_path)

            if not state:
                msg = QApplication.translate("DocumentGenerator",
                                        "Error creating {0}.".format(file_path))
                raise Exception(msg)

    def _export_composition_as_pdf(self, composition, file_path):
        """
        Render the composition as a PDF file.
        """
        status = composition.exportAsPDF(file_path)
        if not status:
            msg = QApplication.translate("DocumentGenerator",
                                        "Error creating {0}".format(file_path))

            raise Exception(msg)

    def _build_file_name(self, data_source, fieldName, fieldValue, data_fields,
                         fileExtension):
        """
        Build a file name based on the values of the specified data fields.
        """
        table, results = self._exec_query(data_source,fieldName, fieldValue)

        if len(results) > 0:
            rec = results[0]

            ds_values = []

            for dt in data_fields:
                f_value = getattr(rec, dt, '')

                #Get display value
                display_value = \
                    self._file_name_value_formatter.column_display_value(
                        dt,
                        f_value
                    )
                ds_values.append(display_value)

            return "_".join(ds_values) + "." + fileExtension

        return ""

    def _exec_query(self, dataSourceName, queryField, queryValue):
        """
        Reflects the data source then execute the query using the specified
        query parameters.
        Returns a tuple containing the reflected table and results of the query.
        """
        meta = MetaData(bind=STDMDb.instance().engine)
        dsTable = Table(dataSourceName, meta, autoload=True)
        try:
            if not queryField and not queryValue:
                #Return all the rows; this is currently limited to 100 rows
                results = self._dbSession.query(dsTable).limit(100).all()

            else:
                if isinstance(queryValue, str):
                    queryValue = "'{0}'".format(queryValue)
                sql = "{0} = :qvalue".format(queryField)
                results = self._dbSession.query(dsTable).filter(sql).params(qvalue=queryValue).all()

            return dsTable, results
        except SQLAlchemyError as ex:
            self._dbSession.rollback()
            raise ex


    def _composer_output_path(self):
        """
        Returns the directory name of the composer output directory.
        """
        regConfig = RegistryConfig()
        keyName = "ComposerOutputs"

        valueCollection = regConfig.read([keyName])

        if len(valueCollection) == 0:
            return None

        else:
            return valueCollection[keyName]

    def _composeritem_value_handler(self, composer_item, value):
        """
        Factory for setting values based on the composer item type and value.
        """
        if isinstance(composer_item,QgsLayoutItemLabel):
            # if value is None:
            #     composer_item.setText("")
            #     return
            #
            # if isinstance(value, Number):
            #     composer_item.setText("%d"%(value,))
            #     return
            #
            # if isinstance(value, basestring):
            #     composer_item.setText(value)
            #     return
            #
            # if isinstance(value, date):
            #     composer_item.setText(str(value))
            #
            #     return

            label_text =composer_item.text()

            if value is None:
                data_text = label_text[label_text.find('[')+1:label_text.find(']')]
                composer_item.setText(label_text.replace('[{}]'.format(data_text), ''))
                return

            else:
                data_text = label_text[
                            label_text.find('[') + 1:label_text.find(']')]
                if isinstance(value, Number):
                    value = str(value)
                if isinstance(value, bool):
                    if value:
                        value = QApplication.translate(
                            'DocumentGenerator', 'Yes'
                        )
                    else:
                        value = QApplication.translate(
                            'DocumentGenerator', 'No'
                        )
                if isinstance(value, date):
                    value = str(value)

                if isinstance(value, datetime):
                    value = str(value)

                composer_item.setText(
                    label_text.replace('[{}]'.format(data_text), value)
                )
                return

        #Composer picture requires the absolute file path
        elif isinstance(composer_item, QgsLayoutItemPicture):
            if value:
                composer_item.setPictureFile(value)



