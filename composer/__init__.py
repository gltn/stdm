"""
Package that enables the customization of the map composer to create custom reports and documents.
"""
from .composer_wrapper import ComposerWrapper
from .composer_item_config import (
                                   ComposerItemConfig,
                                   DataLabelConfig,
                                   LineItemConfig,
                                   ManageTemplatesConfig,
                                   MapConfig,
                                   OpenTemplateConfig,
                                   SaveTemplateConfig
                                   )
from .item_formatter import (
                             BaseComposerItemFormatter,
                             LineFormatter,
                             DataLabelFormatter,
                             MapFormatter
                             )
from .composer_data_source import ComposerDataSource
from .document_generator import DocumentGenerator
from .spatial_fields_config import SpatialFieldsConfiguration