from collections import OrderedDict



class STRDataStore():
    def __init__(self):
        self.party = OrderedDict()
        self.spatial_unit = OrderedDict()
        self.str_type = OrderedDict()
        self.supporting_document = []
        self.source_doc_manager = None

    def remove_party_data(self, id):
        del self.party[id]

    def remove_spatial_data(self, id):
        del self.spatial_unit[id]


    def remove_str_type_data(self, party_id):
        del self.str_type[party_id]
