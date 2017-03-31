# Change Log
All notable changes of the Social Tenure Domain Model(STDM) is documented in this file.


## [1.5.2] - 2017-03-31
### Fixed
- **Spatial Entity Forms**: Fixed error when submitting unfilled required fields.

## [1.5.1] - 2017-03-15
### Fixed
- **Database and Configuration**: Fixed inability to append profile prefix on entity
with similar name as the profile.
- **Supporting Documents**: Fixed the error when saving supporting documents on
entities with no profile prefix.

### Changed
- **Change Log**: Updated the change log.

## [1.5.0] - 2017-02-23

### Added
- **Database and Configuration**: Draft Configuration that enable users save their
configuration without committing to the database.
- **Database and Configuration**: Copy Profile that enables users to create a copy
of existing profiles, rename them and customize them.
- **Database and Configuration**: Percent Column type to store percentage data.
- **Database and Configuration**: Auto Generated Code Column type to generate
 unique code data.
- **Database and Configuration**: Ability to set more than one entities as party entity.
- **Database and Configuration**: Tenure Validity Period to specify tenure agreement period.
- **Database and Configuration**: Tenure Share to set right share on a spatial unit.
- **Database and Configuration**: Created two groups of STR views. Spatial Unit view containing
geometry and party views containing Party and Tenure information.
- **Database and Configuration**: visual representation diagram generated for
a created STR with the ability to export the diagram as an image.
- **Database and Configuration**: ability to enable PostGIS extension
if PostGIS is installed.
- **Current Profile Selection**: combobox in STDM Toobar to select the current profile.
- **Social Tenure Relationship Editor**: the ability to save multiple STR entries at once.
- **Social Tenure Relationship Editor**: combobox to change party entity.
- **Social Tenure Relationship Editor**: Local Spatial Unit preview.
- **Social Tenure Relationship Editor**: Tenure share entry in Tenure Information.
- **Social Tenure Relationship Editor**: Tenure Validity Period entry.
- **View Social Tenure Relationship**: search filter based on tenure validity period.
- **GPS Feature Import**: Ability to edit coordinates.
- **GPS Feature Import**: Automatic update of preview feature on modification of coordinates.
- **GPS Feature Import**: Sorting of coordinate through drag and drop.
- **GPS Feature Import**: Highlighting of points when the corresponding row is selected.
- **GPS Feature Import**: Ability to edit the latitude and longitude values in GPX Data table.
- **Spatial Entity Details**: A module that displays feature data on them map
when features are clicked.
- **Entity Browser**: Spatial Entity Browser can select multiple features
when multiple rows are selected.
- **Entity Browser**: ability to view STR of a selected spatial unit record
while Spatial Entity Details is open.
- **Import Data**: Simpler lookup value translation using Lookup Value Translator.
- **Documents Designer**: Upgraded QgsComposerAttributeTableV2 to incorporate
the the appearance options in attribute table Item Properties panel.
- **Options**: ability to enable and disable debugging mode in STDM.
- **General**: Added startup.py to go into .qgis python folder to enable STDM if disabled by QGIS.
The startup.py and startup_handler.py are both located in settings folder of STDM.

### Changed
- **Database and Configuration**: Enhanced input validation on Profile, Entity,
Column, Lookup and Lookup Value Editors.
- **Database and Configuration**: After adding and editing a column, the column modified
gets selected after the Column Editor is closed to easily show the changed column instead of
clearing the selection.
- **Database and Configuration**: When adding a new column, the column view scrolls to the new column.
If the column is edited, the scroll position doesn't changed after closing the Column Editor.
- **GPS Feature Import**: Re-designed with the integration of GPS file upload,
GPX Data Editor, and STDM Form in a tab interface.
- **Social Tenure Relationship Editor**: re-designed with a tree view interface.
- **Forms**: The Collection tab used to select records from child entities is removed.
- **Forms**: In parent entity, child entity browsers with editor are added.
This enables users to add a record for child entities within parent form.
- **User Manual**: updated with contents of STDM 1.5 with improved readability.

### Fixed
- **Database and Configuration**: Fixed Configuration Wizard Entity order mismatch
 error when deleting an Entity.
- **Database and Configuration**: Fixed issue of showing columns of deleted entity.
- **Database and Configuration**: Fixed the change of column order when editing columns.
- **Users and Roles**: When creating roles, permission is automatically give to sequences too.
- **GPS Feature Import**: Fixed issue of distortion of coordinates in GPS
Feature Import tool.

## [1.4.3] - 2017-01-22

### Changed
- **Database and Configuration**: Removed drag and drop sort from Profile
Entities table of the **Configuration Wizard** as it has no effect on the
actual order.

### Fixed
- **Database and Configuration**: Fixed the issue of not selecting the previously
set party entity in the Configuration Wizard.
- **Spatial Unit Manager**: Fixed the inability to re-name view layer rename
using the spatial unit manager.
- **Supporting Documents**: Fixed the inability to upload supporting document
files with accents/diacritics.
- **Social Tenure Relationship Editor**: Fixed error in the Social Tenure
Relationship wizard for configurations with related entity columns in party
or spatial units.
