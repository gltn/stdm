from stdm.settings import current_profile
from stdm.data.configuration import entity_model


cp = current_profile()

scheme_entity = cp.entity('Scheme')
# holders_entity = cp.entity('Holder')

x = entity_model(scheme_entity)

y = x()

y.scheme_name = "karis"
y.date_of_approval = "2019-07-11"
y.date_of_establishment = "2019-07-11"
y.relevant_authority = 1
y.land_rights_office = 1
y.region = 10
y.title_number = 'ASDFGT'
y.township_name = 3
y.registration = 9
y.area = 20.1
y.doc_imposing_conditions_no = "123QWE"
y.constitution_ref_no = "QWE780"
y.no_of_plots = "20"
y.scheme_number = "12345RT"

y.save()




