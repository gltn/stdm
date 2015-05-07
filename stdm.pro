SOURCES = stdm.py \
			ui/view_str.py \
			navigation/components.py \
			security/membership.py \
			ui/about.py \
			ui/addtable.py \
			ui/admin_unit_manager.py \
			ui/admin_unit_selector.py \
			ui/attribute_editor.py \
			ui/change_pwd_dlg.py \
			ui/composer_data_source.py \
			ui/composer_doc_selector.py \
			ui/composer_field_selector.py \
			ui/composer_spcolumn_styler.py \
			ui/composer_symbol_editor.py \
			ui/content_auth_dlg.py \
			ui/db_conn_dlg.py \
			ui/entity_browser.py \
			ui/export_data.py \
			ui/fkbase_form.py \
			ui/foreign_key_editors.py \
			ui/foreign_key_mapper.py \
			ui/frmAbout.py \
			ui/geometry_editor.py \
			ui/geometry.py \
			ui/import_data.py \
			ui/login_dlg.py \
			ui/lookup_values_dlg.py \
			ui/lookupDlg.py \
			ui/manage_accounts_dlg.py \
			ui/new_role_dlg.py \
			ui/new_str_wiz.py \
			ui/new_user_dlg.py \
			ui/notification.py \
			ui/person_doc_generator.py \
			ui/profileDlg.py \
			ui/propertyPreview.py \
			ui/sourcedocument.py \
			ui/stdmdialog.py \
			ui/str_editor_dlg.py \
			ui/table_propertyDlg.py \
			ui/ui_about_stdm.py \
			ui/ui_about_stdm2.py \
			ui/ui_admin_details.py \
			ui/ui_admin_unit.py \
			ui/ui_adminUnitManager.py \
			ui/ui_attribute_editor.py \
			ui/ui_base_form.py \
			ui/ui_base_person.py \
			ui/ui_changepwd.py \
			ui/ui_composer_data_field.py \ 
			ui/ui_composer_data_source.py \
			ui/ui_composer_doc_selector.py \
			ui/ui_composer_spcolumn_styler.py \
			ui/ui_composer_symbol_editor.py \
			ui/ui_content_auth.py \
			ui/ui_coordinates_editor.py \
			ui/workspace_config.py\
			ui/ui_dbconn.py \
			ui/ui_dbmanage.py \
			ui/ui_doc_item.py \
			ui/ui_entity_browser.py \
			ui/ui_export_data.py \
			ui/ui_farmer.py \
			ui/ui_food_crop_editor.py \
			ui/ui_foreign_key_mapper.py \
			ui/ui_garden_editor.py \
			ui/ui_genericAdminUnitManager.py \
			ui/ui_household.py 
			ui/import_data.py \
			ui/ui_login.py \
			ui/ui_login.py \
			ui/ui_lookup.py \
			ui/ui_main_widget.py \
			ui/ui_new_role.py \
			ui/ui_new_str.py \
			ui/ui_new_user.py \
			ui/ui_notif_item.py \
			ui/ui_person_doc_generator.py \
			ui/ui_profile.py \
			ui/ui_property_preview.py \
			ui/ui_str_editor.py \
			ui/ui_str_view_entity.py \
			ui/ui_survey.py \
			ui/ui_table.py \
			ui/ui_table_property.py \
			ui/ui_user_role_manage.py \
			ui/ui_view_str.py \
			ui/ui_workspace_config.py\
			utils/case_insensitive_dict.py\
			utils/filesize.py \
			utils/hashable_mixin.py \
			utils/reverse_dict.py \
			utils/util.py 
			composer/spatial_fields_config.py \
			composer/item_formatter.py \
			composer/document_generator.py \
			composer/composer_wrapper.py \
			composer/composer_item_config.py \
			composer/composer_data_source.py \
			settings/path_settings.py \
			settings/projectionSelector.py \
			settings/registryconfig.py \
			settings/tools_network.py \
			security/user.py \
			security/roleprovider.py \
			security/membership.py \
			security/exception.py\
			security/authorization.py \
			network/filemanager.py \
			navigation/treeloader.py \
			navigation/signals.py \
			navigation/propertybrowser.py \
			navigation/content_group.py \
			navigation/container_loader.py \
			navigation/components.py \
			mapping/utils.py \
			mapping/editor_config.py \
			mapping/edit_tool.py \
			mapping/create_feature.py \
			mapping/capture_tool.py \
			data/config.py \
			data/config_table_reader.py \
			data/config_utils.py \
			data/configfile_paths.py \
			data/connection.py \
			data/data_reader_form.py \
			data/database.py \
			data/enums.py \
			data/globals.py\
			data/license_doc.py \
			data/lookups.py \
			data/mapping.py \
			data/modelformatters.py \
			data/pg_utils.py \
			data/qtmodels.py \
			data/template_database.py \
			data/usermodels.py \
			data/xmlconfig_reader.py \
			data/xmlconfig_writer.py \
			data/xmldata2sql.py \
			ui/ui_base_form.py
					
FORMS =	ui/reports/ui_rpt_builder.ui \
		ui/ui_changepwd.ui \	
  	 	ui/ui_dbconn.ui \
		ui/ui_dbmanage.ui \
		ui/ui_login.ui \
		ui/ui_user_role_manage.ui \
		ui/ui_admin_details.ui \
		ui/ui_attribute_editor.ui \
		ui/ui_combo_option_other.ui \
		ui/ui_composer_data_field.ui \ 
		ui/ui_composer_data_source.ui \
		ui/ui_composer_doc_selector.ui \
		ui/ui_composer_spcolumn_styler.ui \
		ui/ui_composer_symbol_editor.ui \
		ui/ui_configWizard.ui \
		ui/ui_content_auth.ui \
		ui/ui_coordinates_editor.ui \
		ui/ui_doc_item.ui \
		ui/ui_entity_browser.ui \
		ui/ui_export_data.ui \
		ui/ui_foreign_key_mapper.ui \
		ui/ui_genericAdminUnitManager.ui \
		ui/ui_import_data.ui \
		ui/ui_lookup_source.ui \
		ui/ui_main_widget.ui \
		ui/ui_new_role.ui \
		ui/ui_new_str.ui \
		ui/ui_new_user.ui \
		ui/ui_notif_item.ui \
		ui/ui_person_doc_generator.ui \
		ui/ui_profile.ui \
		ui/ui_property_preview.ui \
		ui/ui_table_property.ui \
		ui/ui_table.ui \
		ui/ui_str_editor.ui \
		ui/ui_str_view_entity.ui \
		ui/ui_view_str.ui \
		ui/ui_view_str_search_entity.ui \
		ui/ui_base_form.ui
	
TRANSLATIONS    = i18n/stdm_fr.ts 

CODECFORTR      = UTF-8 

CODECFORSRC     = UTF-8 