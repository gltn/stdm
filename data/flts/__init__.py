from .readers import (
    xls_2_qgs_vector_layer
)


# Functions that return the holders' data source based on the data source file type
holder_readers = {
    'xls': xls_2_qgs_vector_layer,
    'xlsx': xls_2_qgs_vector_layer,
    'csv': None
}