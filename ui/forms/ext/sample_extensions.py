from PyQt4.QtCore import Qt

from stdm.ui.forms.editor_extension import (
    AbstractEditorExtension,
    cascading_field_ctx,
    data_context
)


# Context - Customize widget properties
# Person entity in Local Government profile
@data_context('Local Government Profile', 'Person')
class PersonEditorExtension(AbstractEditorExtension):
    def post_init(self):
        # Override method which is called immediately after the
        # parent’s __init__ has been executed
        income_widget = self.widget('income')
        # Add dollar sign to show currency
        income_widget.setPrefix('$')


# Context - Automatically compute a value based on user input
# Household entity in Informal Settlement profile
@data_context('Informal Settlement Profile', 'Household')
class HouseholdEditorExtension(AbstractEditorExtension):
    def post_init(self):
        num_child_widget = self.widget('number_of_children')
        # Connect signal to calculate compensation when number of
        # children changes
        num_child_widget.valueChanged.connect(self.on_num_child_changed)

        # Reference to compensation widget
        self.compensation_txt = self.widget('compensation')

        # Disable user input as value is automatically computed
        self.compensation_txt.setEnabled(False)

    def on_num_child_changed(self, num_children):
        # Slot raised when the number of children changes.
        compensation = self.calc_compensation(num_children)
        self.compensation_txt.setText(compensation)

    def calc_compensation(self, num_children):
        """
        Computes value of compensation based on number of childre.
        :param name: Number of children.
        :type name: int
        :return: Returns the compensation value.
        :rtype: float
        """
        pass


# Context - Send notifications to the parent editor form
# Farmer entity in Rural Agriculture profile
@data_context('Rural Agriculture Profile', 'Farmer')
class FarmerEditorExtension(AbstractEditorExtension):
    def post_init(self):
        self.priorities_widget = self.widget('priorities')
        p_model = self.priorities_widget.item_model

        # Connect signal when a priority is (un)checked
        p_model.itemChanged.connect(self.on_priority_changed)

    def on_priority_changed(self, p_item):
        # Slot raised a priority is checked or unchecked. Limit to 3.
        if len(self.priorities_widget.selection()) > 3:
            # Uncheck the priority item
            p_item.setCheckState(Qt.Unchecked)

            # Insert notification in parent editor
            msg = 'Maximum number of allowed priorities is 3.'
            self.insert_warning_notification(msg)


# Context - Incorporate custom validation before saving form data
# Person entity in Local Government profile
@data_context('Local Government Profile', 'Person')
class PersonEditorExtension(AbstractEditorExtension):
    def post_init(self):
        self.tel_widget = self.widget('telephone')

    def is_telephone_valid(self, tel_num):
        # Custom logic to validate number
        return False

    def validate(self):
        # Override base class method to incorporate custom validation logic.
        # It must return True or False
        tel_num = self.tel_widget.text()
        is_valid = self.is_telephone_valid(tel_num)
        if not is_valid:
            self.insert_warning_notification('Invalid telephone number')

        return is_valid


# Context - Specify conditional visibility of widgets based on user input
# Person entity in Local Government profile
@data_context('Local Government Profile', 'Person')
class PersonEditorExtension(AbstractEditorExtension):
    def post_init(self):
        self.m_status_cbo = self.widget('marital_status')
        self.m_status_cbo.currentIndexChanged.connect(
            self.on_m_status_changed
        )
        self.spouse_name_txt = self.widget('spouse_name')

    def on_m_status_changed(self, m_status):
        # Enable/disable spouse name text widget based on marital status
        if m_status == 'Married':
            self.spouse_name_txt.setVisible(True)
        else:
            self.spouse_name_txt.clear()
            self.spouse_name_txt.setVisible(False)


# Context - Define cascading comboboxes
# House entity in rural agriculture profile
@data_context('Rural Agriculture Profile', 'House')
class HouseEditorExtension(AbstractEditorExtension):
    def post_init(self):
        # Filter roof materials based on the roof type selected
        # Codes for lookup values SHOULD have been specified
        roof_type_cf_ctx = cascading_field_ctx(
            'roof_type',
            'roof_material',
            ['M', 'B'],
            [
                ('TN', 'CP', 'ZC', 'AL', 'ST'),
                ('FG', 'CL')
            ]
        )

        # Add context to the editor extension
        self.add_cascading_field_context(roof_type_cf_ctx)

