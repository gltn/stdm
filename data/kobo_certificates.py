# -*- coding: utf-8 -*-

from stdm.settings.registryconfig import (
    RegistryConfig,
    backup_path,
    IMPORT_MAPFILE,
    NETWORK_DOC_RESOURCE
)
from stdm.settings import (
    current_profile
)
from PyQt4.QtGui import (
    QApplication,
    QMessageBox
)
from stdm.data.pg_utils import(
    fetch_from_table,
    fetch_with_filter,
    _execute,
    pg_table_exists,
    pg_table_column_exists,
    pg_parent_supporting_document_exists,
    get_value_by_column,
    pg_create_supporting_document,
    pg_create_parent_supporting_document
)

import json
import os
import shutil
import io
import subprocess
import hashlib
from datetime import datetime

from stdm.data.stdm_reqs_sy_ir import fix_auto_sequences

def init_export_configfile():
    data = {
        "out_folder": "C:\\TEMP3\\sss3\\claims",
        "split_by_doctype": "True",
	    "dataset": "hl_property",
	    "fld_id": "id",
        "fld_result": "claim_ref_number",
        "ds_doc": "hl_property_supporting_document",
        "ds_doc_key": "property_id",
        "ds_doc_typeid": "document_type",
        "ds_doc_result": "supporting_doc_id",
        "doc": "hl_supporting_document",
        "doc_key": "id",
        "doc_fld_filename" : "filename",
        "doc_fld_hashname" : "document_identifier",
        "doc_result" : "filename",
        "ds_doctype": "hl_check_property_document_type",
        "ds_doctype_key": "id",
        "ds_doctype_result": "value"
    }
    logs=[]
    logs.append(data)
    write_info(logs, get_config_filename())
    return

def get_entity_config(entities, index):
    entity_config = {"inited": "False"}
    if index < 0:
        return entity_config
    if entities is None:
        return entity_config
    if index >= len(entities):
        return entity_config
    entity_config = {
        "initied" : "True",
        "out_folder": entities[index]['out_folder'],
        "split_by_doctype": entities[index]['split_by_doctype'],
        "dataset": entities[index]['dataset'],
        "fld_id": entities[index]['fld_id'],
        "fld_result": entities[index]['fld_result'],
        "ds_doc": entities[index]['ds_doc'],
        "ds_doc_key": entities[index]['ds_doc_key'],
        "ds_doc_typeid": entities[index]['ds_doc_typeid'],
        "ds_doc_result": entities[index]['ds_doc_result'],
        "doc": entities[index]['doc'],
        "doc_key": entities[index]['doc_key'],
        "doc_fld_filename" : entities[index]['doc_fld_filename'],
        "doc_fld_hashname": entities[index]['doc_fld_hashname'],
        "doc_result": entities[index]['doc_result'],
        "ds_doctype": entities[index]['ds_doctype'],
        "ds_doctype_key": entities[index]['ds_doctype_key'],
        "ds_doctype_result" : entities[index]['ds_doctype_result']
    } 
    return entity_config

def whereclause_from_fieldandvalue(fld, val):
    return 'WHERE {}={}'.format(fld, val)

def dataset_filter(dsname, whereclause):
    wrclause = ' {};'.format(whereclause)
    qry = 'SELECT * FROM {}{}'.format(
        dsname,
        wrclause
    )
    return fetch_with_filter(qry)

def enum_doctypes(dsname, fld_typeid, fld_type):
    doctypes = []
    cdoctypes = fetch_from_table(dsname, 'null')
    for doctype in cdoctypes:
        doctypes.append(
            {
                "id": str(doctype[fld_typeid]),
                "type": doctype[fld_type]         
            }
        )
    return doctypes

def get_doctype_by_id( doctypes, id ):
    for doctype in doctypes:
        if doctype["id"] == str(id):
            return doctype["type"]
    return ""

def check_docpath_by_doctype(doc_path, profile, dataset, doc_type):
    temp_result = '{}\\{}\\{}\\{}'.format( 
        doc_path,
        profile.name.lower(),
        dataset,
        doc_type
    )
    if os.path.exists(temp_result):
        return temp_result
    temp_result = '{}\\{}\\{}\\{}'.format( 
        doc_path,
        profile.name.lower(),
        dataset,
        doc_type.replace(' ', '_')
    )
    if os.path.exists(temp_result):
        return temp_result
    return ''
    

def claims_export():
    configs = read_export_configfile(get_config_filename())
    entity_config = get_entity_config(configs, 0)
    doc_path = get_document_path()
    
    doctypes = enum_doctypes(
        entity_config['ds_doctype'],
        entity_config['ds_doctype_key'],
        entity_config['ds_doctype_result']
    )
    
    claims = fetch_from_table(entity_config['dataset'], 'null')
    for clm in claims:
        foldername = clm[entity_config['fld_result']]
        foldername_full =  '{}\\{}'.format(
            entity_config['out_folder'],
            foldername
        )
        if not os.path.exists(foldername_full):
            os.makedirs(foldername_full)

        cdocs = dataset_filter(
            entity_config['ds_doc'],
            whereclause_from_fieldandvalue(
                entity_config['ds_doc_key'],
                clm[entity_config['fld_id']]
            )
        )
        for cdoc in cdocs:
            doc_type = get_doctype_by_id(
                doctypes,
                str(cdoc[entity_config['ds_doc_typeid']])
            )

            srcfile_path = check_docpath_by_doctype( 
                doc_path,
                current_profile(),
                entity_config['dataset'],
                doc_type
            )
            if not os.path.exists(srcfile_path):
                continue
            docs = dataset_filter(
                entity_config['doc'],
                whereclause_from_fieldandvalue(
                    entity_config['doc_key'],
                    cdoc[entity_config['ds_doc_result']]
                )
            )
            for doc in docs:
                doc_name = doc[entity_config['doc_fld_filename']]
                doc_hname = doc[entity_config['doc_fld_hashname']]
                doc_filename, doc_fileext = os.path.splitext(
                    doc_name
                )
                out_filename, out_fileext = os.path.splitext(
                    doc[entity_config['doc_result']]
                )
                src_docname = '{}\{}{}'.format(
                    srcfile_path,
                    doc_hname,
                    doc_fileext
                )
                dest_path = foldername_full
                if entity_config['split_by_doctype'].lower() == 'true':
                    dest_path = '{}\{}'.format(
                        foldername_full,
                        doc_type
                    )
                
                dest_docname =  '{}\{}{}'.format(
                    dest_path,
                    out_filename,
                    doc_fileext
                )
                if os.path.exists(src_docname):
                    if not os.path.exists(dest_docname):       
                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path)
                        shutil.copy(src_docname, dest_docname)
 
    ErrMessage('Done Successfully')
    return

def evidences_export():
    configs = read_export_configfile(get_config_filename())
    entity_config = get_entity_config(configs, 1)
    doc_path = get_document_path()
    
    doctypes = enum_doctypes(
        entity_config['ds_doctype'],
        entity_config['ds_doctype_key'],
        entity_config['ds_doctype_result']
    )
    
    claims = fetch_from_table(entity_config['dataset'], 'null')
    for clm in claims:
        foldername = clm[entity_config['fld_result']]
        foldername_full =  '{}\\{}'.format(
            entity_config['out_folder'],
            foldername
        )
        if not os.path.exists(foldername_full):
            os.makedirs(foldername_full)

        cdocs = dataset_filter(
            entity_config['ds_doc'],
            whereclause_from_fieldandvalue(
                entity_config['ds_doc_key'],
                clm[entity_config['fld_id']]
            )
        )
        for cdoc in cdocs:
            doc_type = get_doctype_by_id(
                doctypes,
                str(cdoc[entity_config['ds_doc_typeid']])
            )
            
            srcfile_path = check_docpath_by_doctype( 
                doc_path,
                current_profile(),
                entity_config['dataset'],
                doc_type
            )
            if not os.path.exists(srcfile_path):
                continue
            docs = dataset_filter(
                entity_config['doc'],
                whereclause_from_fieldandvalue(
                    entity_config['doc_key'],
                    cdoc[entity_config['ds_doc_result']]
                )
            )
            for doc in docs:
                doc_name = doc[entity_config['doc_fld_filename']]
                doc_hname = doc[entity_config['doc_fld_hashname']]
                doc_filename, doc_fileext = os.path.splitext(
                    doc_name
                )
                out_filename, out_fileext = os.path.splitext(
                    doc[entity_config['doc_result']]
                )
                src_docname = '{}\{}{}'.format(
                    srcfile_path,
                    doc_hname,
                    doc_fileext
                )
                dest_path = foldername_full
                if entity_config['split_by_doctype'].lower() == 'true':
                    dest_path = '{}\{}'.format(
                        foldername_full,
                        doc_type
                    )
                
                dest_docname =  '{}\{}{}'.format(
                    dest_path,
                    out_filename,
                    doc_fileext
                )
                if os.path.exists(src_docname):
                    if not os.path.exists(dest_docname):       
                        if not os.path.exists(dest_path):
                            os.makedirs(dest_path)
                        shutil.copy(src_docname, dest_docname)
 
    ErrMessage('Done Successfully')
    return

def get_config_filename():
    reg_config = RegistryConfig()
    mapfile = reg_config.read([IMPORT_MAPFILE])
    import_mapfile = mapfile.get(IMPORT_MAPFILE, '')
    config_path = os.path.dirname(import_mapfile)
    config_file = config_path + '\\' + 'claims_export_config.json'
    return config_file

def get_document_path():
    reg_config = RegistryConfig()
    support_doc_path = reg_config.read([NETWORK_DOC_RESOURCE])
    doc_path = support_doc_path.values()[0]
    return doc_path

def read_export_configfile(conf_file):
    logs = [] 
    if not os.path.exists(conf_file):
        return logs
    if os.path.getsize(conf_file) == 0:
        return logs
    with open(conf_file) as data_file:
        logs = json.load(data_file)
    return logs

def write_info(data, out_file):
    if len(data) == 0:
        return
    with open(out_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
"""
all the following functions will be replaced with new functions 
which read datasets names and fields names from config file
The code here is the initial scripts to create kobo certificates 
"""
def find_enumerator(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS enumerator_id'\
                    ', {} AS enumerator_name'\
                    ', {} AS enumeration_date'\
                    ', {} AS enumeration_location'\
                    ', {} AS enumeration_location_lat'\
                    ', {} AS enumeration_location_long'\
                    ', {} AS enumeration_location_att'\
                    ', {} AS enumeration_location_acc'\
                    ', {} AS consent_approval'\
                    ', {} AS consent_refuse_reason'\
                    ', {} AS consent_refuse_reason_other'\
                    ', {} AS respondent_gender'\
                    ' FROM {}{}'.format(
                        'hl_enumeration.kobo_id', 
                        'hl_enumeration.id', 
                        'hl_check_enumerator.value', 
                        'hl_enumeration.enumeration_date', 
                        'hl_check_enumeration_area_name.value',
                        'hl_enumeration.map_lat', 
                        'hl_enumeration.map_lon', 
                        'hl_enumeration.map_alt', 
                        'hl_enumeration.map_pre', 
                        #'hl_enumeration.respondent_consent', 
                        'hl_check_consent.value', 
                        'hl_check_refuse_submit_claim.value', #
                        'hl_enumeration.other_reason_of_refuse', 
                        'hl_check_gender.value',

                        'hl_enumeration'\
                        ' LEFT JOIN hl_check_enumerator ON hl_enumeration.enumerator_name = hl_check_enumerator.id'\
                        ' LEFT JOIN hl_check_enumeration_area_name ON hl_enumeration.enumeration_area_name = hl_check_enumeration_area_name.id'\
                        ' LEFT JOIN hl_check_consent ON hl_enumeration.respondent_consent = hl_check_consent.id'\
                        ' LEFT JOIN hl_check_refuse_submit_claim ON hl_enumeration.refuse_submit_claim = hl_check_refuse_submit_claim.id'\
                        ' LEFT JOIN hl_check_gender ON hl_enumeration.respondent_gender = hl_check_gender.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'enumerator_id':u'{}'.format(rec['enumerator_id']),
                    'enumerator_name':u'{}'.format(rec['enumerator_name']),
                    'enumeration_date':u'{}'.format(rec['enumeration_date']),
                    'enumeration_location':u'{}'.format(rec['enumeration_location']),
                    'enumeration_location_lat':u'{}'.format(rec['enumeration_location_lat']),
                    'enumeration_location_long':u'{}'.format(rec['enumeration_location_long']),
                    'enumeration_location_att':u'{}'.format(rec['enumeration_location_att']),
                    'enumeration_location_acc':u'{}'.format(rec['enumeration_location_acc']),
                    'consent_approval':u'{}'.format(rec['consent_approval']),
                    'consent_refuse_reason':u'{}'.format(rec['consent_refuse_reason']),
                    'consent_refuse_reason_other':u'{}'.format(rec['consent_refuse_reason_other']),
                    'respondent_gender':u'{}'.format(rec['respondent_gender'])
                }
            )
    return result_as_array

def find_respondent(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS respondent_id'\
                    ', {} AS respondent_first_name'\
                    ', {} AS respondent_last_name'\
                    ', {} AS respondent_father_name'\
                    ', {} AS respondent_mother_name'\
                    ', {} AS respondent_mobile_number'\
                    ', {} AS respondent_whatsapp_number'\
                    ', {} AS respondent_email'\
                    ', {} AS respondent_gender'\
                    ', {} AS respondent_birthdate'\
                    ', {} AS respondent_address'\
                    ', {} AS respondent_education'\
                    ', {} AS respondent_yearofleave'\
                    ', {} AS respondent_numberofdisplacements'\
                    ', {} AS respondent_photo'\
                    ', {} AS household_group_photo'\
                    ', {} AS enumerator_id'\
                    ' FROM {}{}'.format(
                        'hl_respondent.kobo_id', 
                        'hl_respondent.id', 
                        'hl_respondent.first_name', 
                        'hl_respondent.last_name', 
                        'hl_respondent.fathers_name',
                        'hl_respondent.mothers_name', 
                        'hl_respondent.mobile_number', 
                        'hl_respondent.whatsapp_number', 
                        'hl_respondent.email_address', 
                        'hl_check_gender.value', 
                        'hl_respondent.birth_date', 
                        'hl_respondent.current_physical_address', 
                        'hl_check_education_level_respondent.value',
                        'hl_respondent.ymonth_left_property', 
                        'hl_respondent.displacement_count', 
                        'hl_respondent.respondent_photo', 
                        'hl_respondent.household_photo', 
                        'hl_respondent.enumeration',

                        'hl_respondent'\
                        ' LEFT JOIN hl_check_gender ON hl_respondent.gender = hl_check_gender.id'\
                        ' LEFT JOIN hl_check_education_level_respondent ON hl_respondent.education_level_respondent = hl_check_education_level_respondent.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'respondent_id':u'{}'.format(rec['respondent_id']),
                    'respondent_first_name':u'{}'.format(rec['respondent_first_name']),
                    'respondent_last_name':u'{}'.format(rec['respondent_last_name']),
                    'respondent_father_name':u'{}'.format(rec['respondent_father_name']),
                    'respondent_mother_name':u'{}'.format(rec['respondent_mother_name']),
                    'respondent_mobile_number':u'{}'.format(rec['respondent_mobile_number']),
                    'respondent_whatsapp_number':u'{}'.format(rec['respondent_whatsapp_number']),
                    'respondent_email':u'{}'.format(rec['respondent_email']),
                    'respondent_gender':u'{}'.format(rec['respondent_gender']),
                    'respondent_birthdate':u'{}'.format(rec['respondent_birthdate']),
                    'respondent_address':u'{}'.format(rec['respondent_address']),
                    'respondent_education':u'{}'.format(rec['respondent_education']),
                    'respondent_yearofleave':u'{}'.format(rec['respondent_yearofleave']),
                    'respondent_numberofdisplacements':u'{}'.format(rec['respondent_numberofdisplacements']),
                    'respondent_photo':u'{}'.format(rec['respondent_photo']),
                    'household_group_photo':u'{}'.format(rec['household_group_photo']),
                    'enumerator_id':u'{}'.format(rec['enumerator_id'])
                }
            )
    return result_as_array

def find_household_member(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS household_member_id'\
                    ', {} AS household_member_first_name'\
                    ', {} AS household_member_last_name'\
                    ', {} AS household_member_father_name'\
                    ', {} AS household_member_mother_name'\
                    ', {} AS household_member_relation'\
                    ', {} AS household_member_relation_other'\
                    ', {} AS household_member_education'\
                    ', {} AS household_memebr_birthdate'\
                    ', {} AS household_member_gender'\
                    ', {} AS household_member_right_type'\
                    ', {} AS household_member_right_type_other'\
                    ', {} AS household_member_kobo_index'\
                    ', {} AS respondent_id'\
                    ' FROM {}{}'.format(
                        'hl_household_member.kobo_submission_id', 
                        'hl_household_member.id', 
                        'hl_household_member.first_name', 
                        'hl_household_member.last_name', 
                        'hl_household_member.fathers_name',
                        'hl_household_member.mothers_name', 
                        'hl_check_respondent_relation.value', 
                        'hl_household_member.other_relative', 
                        'hl_check_education_level_members.value', 
                        'hl_household_member.birth_date', 
                        'hl_check_gender.value', 
                        'hl_check_property_right_type.value', 
                        'hl_household_member.other_property_right_type',
                        'hl_household_member.kobo_index',
                        'hl_household_member.respondent',

                        'hl_household_member'\
                        ' LEFT JOIN hl_check_respondent_relation ON hl_household_member.respondent_relation = hl_check_respondent_relation.id'\
                        ' LEFT JOIN hl_check_education_level_members ON hl_household_member.education_level_members = hl_check_education_level_members.id'\
                        ' LEFT JOIN hl_check_gender ON hl_household_member.sex = hl_check_gender.id'\
                        ' LEFT JOIN hl_check_property_right_type ON hl_household_member.property_right_type = hl_check_property_right_type.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'household_member_id':u'{}'.format(rec['household_member_id']),
                    'household_member_first_name':u'{}'.format(rec['household_member_first_name']),
                    'household_member_last_name':u'{}'.format(rec['household_member_last_name']),
                    'household_member_father_name':u'{}'.format(rec['household_member_father_name']),
                    'household_member_mother_name':u'{}'.format(rec['household_member_mother_name']),
                    'household_member_relation':u'{}'.format(rec['household_member_relation']),
                    'household_member_relation_other':u'{}'.format(rec['household_member_relation_other']),
                    'household_member_education':u'{}'.format(rec['household_member_education']),
                    'household_memebr_birthdate':u'{}'.format(rec['household_memebr_birthdate']),
                    'household_member_gender':u'{}'.format(rec['household_member_gender']),
                    'household_member_right_type':u'{}'.format(rec['household_member_right_type']),
                    'household_member_right_type_other':u'{}'.format(rec['household_member_right_type_other']),
                    'household_member_kobo_index':u'{}'.format(rec['household_member_kobo_index']),
                    'respondent_id':u'{}'.format(rec['respondent_id'])
                }
            )
    return result_as_array

def find_claim(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS property_id'\
                    ', {} AS claim_ref_number'\
                    ', {} AS location_is_excact'\
                    ', {} AS location'\
                    ', {} AS location_governorate'\
                    ', {} AS location_district'\
                    ', {} AS location_district_other'\
                    ', {} AS location_subdistrict'\
                    ', {} AS locatin_subdistrict_other'\
                    ', {} AS location_community'\
                    ', {} AS location_fulladdress'\
                    ', {} AS location_cadastral_map_number'\
                    ', {} AS property_damage_by_sattelite'\
                    ', {} AS property_damage_by_owner'\
                    ', {} AS property_occupation'\
                    ', {} AS property_desc'\
                    ', {} AS property_type'\
                    ', {} AS property_land_use'\
                    ', {} AS property_land_use_other'\
                    ', {} AS property_buiding_type'\
                    ', {} AS property_buiding_use'\
                    ', {} AS claimed_rights_type'\
                    ', {} AS claimed_rights_share'\
                    ', {} AS claimed_inheritance'\
                    ', {} AS claimed_inheritance_more_info'\
                    ', {} AS general_comment'\
                    ', {} AS signature'\
                    ', {} AS respondent_id'\
                    ', {} AS property_id_number'\
                    ', {} AS property_location'\
                    ', {} AS kobo_index'\
                    ', {} AS property_qrcode'\
                    ' FROM {}{}'.format(
                        'hl_property.kobo_submission_id', 
                        'hl_property.id', 
                        'hl_property.claim_ref_number', 
                        'hl_check_property_location_type.value', 
                        'hl_property.map_location',
                        'hl_check_governorate.value', 
                        'hl_check_district.value', 
                        'hl_property.other_district', 
                        'hl_check_sub_district.value', 
                        'hl_property.other_sub_district', 
                        'hl_property.community', 
                        'hl_property.property_address', 
                        'hl_property.cadastral_map_number', 
                        'dv1.value', 
                        'dv2.value',
                        'hl_check_property_occupied.value', 
                        'hl_property.property_description', 
                        'hl_check_property_type.value', 
                        'hl_check_land_use_type.value', 
                        'hl_property.other_land_use', 
                        'hl_check_build_type.value', 
                        'hl_check_building_use_type.value', 
                        'hl_check_tenure_type.value', 
                        'hl_property.shares_number', 
                        'hl_check_property_inherited.value', 
                        'hl_property.inheritance_information',
                        'hl_property.general_comments', 
                        'hl_property.signature_filename', 
                        'hl_property.respondent', 
                        'hl_property.property_id_number',
                        'hl_property.property_location',
                        'hl_property.kobo_index',
                        "'CRN:' || {} || '/PID:SY/' || {} || '/' || {} || '/' || {}".format(
                            "COALESCE(hl_property.claim_ref_number, '')",
                            "COALESCE(hl_check_governorate.code, '')",
                            "COALESCE(hl_check_district.code, '')",
                            "COALESCE(hl_property.property_id_number, '')"
                        ),

                        'hl_property'\
                        ' LEFT JOIN hl_check_property_location_type ON hl_property.is_location_exact_approx = hl_check_property_location_type.id'\
                        ' LEFT JOIN hl_check_governorate ON hl_property.governorate = hl_check_governorate.id'\
                        ' LEFT JOIN hl_check_district ON hl_property.district = hl_check_district.id'\
                        ' LEFT JOIN hl_check_sub_district ON hl_property.sub_district = hl_check_sub_district.id'\
                        ' LEFT JOIN hl_check_damage_visibility AS dv1 ON hl_property.satellite_damage_visibility = dv1.id'\
                        ' LEFT JOIN hl_check_damage_visibility AS dv2 ON hl_property.respondent_damage_level = dv2.id'\
                        ' LEFT JOIN hl_check_property_occupied ON hl_property.property_occupied = hl_check_property_occupied.id'\
                        ' LEFT JOIN hl_check_property_type ON hl_property.property_type = hl_check_property_type.id'\
                        ' LEFT JOIN hl_check_land_use_type ON hl_property.land_use_type = hl_check_land_use_type.id'\
                        ' LEFT JOIN hl_check_build_type ON hl_property.build_type = hl_check_build_type.id'\
                        ' LEFT JOIN hl_check_building_use_type ON hl_property.building_use_type = hl_check_building_use_type.id'\
                        ' LEFT JOIN hl_check_tenure_type ON hl_property.claimed_rights_type = hl_check_tenure_type.id'\
                        ' LEFT JOIN hl_check_property_inherited ON hl_property.is_property_inherited = hl_check_property_inherited.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'property_id':u'{}'.format(rec['property_id']),
                    'claim_ref_number':u'{}'.format(rec['claim_ref_number']),
                    'location_is_excact':u'{}'.format(rec['location_is_excact']),
                    'location':u'{}'.format(rec['location']),
                    'location_governorate':u'{}'.format(rec['location_governorate']),
                    'location_district':u'{}'.format(rec['location_district']),
                    'location_district_other':u'{}'.format(rec['location_district_other']),
                    'location_subdistrict':u'{}'.format(rec['location_subdistrict']),
                    'locatin_subdistrict_other':u'{}'.format(rec['locatin_subdistrict_other']),
                    'location_community':u'{}'.format(rec['location_community']),
                    'location_fulladdress':u'{}'.format(rec['location_fulladdress']),
                    'location_cadastral_map_number':u'{}'.format(rec['location_cadastral_map_number']),
                    'property_damage_by_sattelite':u'{}'.format(rec['property_damage_by_sattelite']),
                    'property_damage_by_owner':u'{}'.format(rec['property_damage_by_owner']),
                    'property_occupation':u'{}'.format(rec['property_occupation']),
                    'property_desc':u'{}'.format(rec['property_desc']),
                    'property_type':u'{}'.format(rec['property_type']),
                    'property_land_use':u'{}'.format(rec['property_land_use']),
                    'property_land_use_other':u'{}'.format(rec['property_land_use_other']),
                    'property_buiding_type':u'{}'.format(rec['property_buiding_type']),
                    'property_buiding_use':u'{}'.format(rec['property_buiding_use']),
                    'claimed_rights_type':u'{}'.format(rec['claimed_rights_type']),
                    'claimed_rights_share':u'{}'.format(rec['claimed_rights_share']),
                    'claimed_inheritance':u'{}'.format(rec['claimed_inheritance']),
                    'claimed_inheritance_more_info':u'{}'.format(rec['claimed_inheritance_more_info']),
                    'general_comment':u'{}'.format(rec['general_comment']),
                    'signature':u'{}'.format(rec['signature']),
                    'respondent_id':u'{}'.format(rec['respondent_id']),
                    'property_id_number':u'{}'.format(rec['property_id_number']),
                    'property_location':u'{}'.format(rec['property_location']),
                    'kobo_index':u'{}'.format(rec['kobo_index']),
                    'property_qrcode':u'{}'.format(rec['property_qrcode'])
                }
            )
    return result_as_array

def find_evidence(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS evidence_id'\
                    ', {} AS evidence_type'\
                    ', {} AS evidence_type_other'\
                    ', {} AS evidence_picture_front'\
                    ', {} AS evidence_picture_back'\
                    ', {} AS evidence_number'\
                    ', {} AS respondent_id'\
                    ' FROM {}{}'.format(
                        'hl_evidence.kobo_submission_id', 
                        'hl_evidence.id', 
                        'hl_check_evidence_type.value', 
                        'hl_evidence.other_evidence', 
                        'hl_evidence.picture_front', 
                        'hl_evidence.picture_back', 
                        'hl_evidence.document_number', 
                        'hl_evidence.respondent',
                        
                        'hl_evidence'\
                        ' LEFT JOIN hl_check_evidence_type ON hl_evidence.evidence_type = hl_check_evidence_type.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'evidence_id':u'{}'.format(rec['evidence_id']),
                    'evidence_type':u'{}'.format(rec['evidence_type']),
                    'evidence_type_other':u'{}'.format(rec['evidence_type_other']),
                    'evidence_picture_front':u'{}'.format(rec['evidence_picture_front']),
                    'evidence_picture_back':u'{}'.format(rec['evidence_picture_back']),
                    'evidence_number':u'{}'.format(rec['evidence_number']),
                    'respondent_id':u'{}'.format(rec['respondent_id'])
                }
            )
    return result_as_array

def find_lostdoc(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS lost_doc_id'\
                    ', {} AS lost_doc_type'\
                    ', {} AS property_id'\
                    ' FROM {}{}'.format(
                        'hl_lost_documents.id', 
                        'hl_check_lost_document.value', 
                        'hl_lost_documents.hl_property_id', 
                                               
                        'hl_lost_documents'\
                        ' LEFT JOIN hl_check_lost_document ON hl_lost_documents.hl_check_lost_document_id = hl_check_lost_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'lost_doc_id':u'{}'.format(rec['lost_doc_id']),
                    'lost_doc_type':u'{}'.format(rec['lost_doc_type']),
                    'property_id':u'{}'.format(rec['property_id'])
                }
            )
    return result_as_array

def find_respondent_id_doc(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS id_doc_id'\
                    ', {} AS respondent_id_doc_type'\
                    ', {} AS respondent_id_doc_type_other'\
                    ', {} AS respondent_id_doc_number'\
                    ', {} AS respondent_id_doc_date'\
                    ', {} AS respondent_id_doc_front'\
                    ', {} AS respondent_id_doc_back'\
                    ', {} AS respondent_id'\
                    ' FROM {}{}'.format(
                        'hl_respondent_document.kobo_submission_id', 
                        'hl_respondent_document.id', 
                        'hl_check_identification_document.value', 
                        'hl_respondent_document.other_id_document_type', 
                        'hl_respondent_document.id_document_number', 
                        'hl_respondent_document.issue_date', 
                        'hl_respondent_document.id_document_front', 
                        'hl_respondent_document.id_document_back', 
                        'hl_respondent_document.respondent', 
                                               
                        'hl_respondent_document'\
                        ' LEFT JOIN hl_check_identification_document ON hl_respondent_document.id_document_type = hl_check_identification_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'id_doc_id':u'{}'.format(rec['id_doc_id']),
                    'respondent_id_doc_type':u'{}'.format(rec['respondent_id_doc_type']),
                    'respondent_id_doc_type_other':u'{}'.format(rec['respondent_id_doc_type_other']),
                    'respondent_id_doc_number':u'{}'.format(rec['respondent_id_doc_number']),
                    'respondent_id_doc_date':u'{}'.format(rec['respondent_id_doc_date']),
                    'respondent_id_doc_front':u'{}'.format(rec['respondent_id_doc_front']),
                    'respondent_id_doc_back':u'{}'.format(rec['respondent_id_doc_back']),
                    'respondent_id':u'{}'.format(rec['respondent_id'])
                }
            )
    return result_as_array

def find_household_member_id_doc(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS kobo_id'\
                    ', {} AS household_member_id_doc_id'\
                    ', {} AS household_member_id_doc_type'\
                    ', {} AS household_member_id_doc_type_other'\
                    ', {} AS household_member_id_doc_number'\
                    ', {} AS household_member_id'\
                    ' FROM {}{}'.format(
                        'hl_household_member_document.kobo_submission_id', 
                        'hl_household_member_document.id', 
                        'hl_check_identification_document.value', 
                        'hl_household_member_document.other_id_document', 
                        'hl_household_member_document.id_document_number', 
                        'hl_household_member_document.household_member', 
                                               
                        'hl_household_member_document'\
                        ' LEFT JOIN hl_check_identification_document ON hl_household_member_document.id_document_type = hl_check_identification_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'kobo_id':u'{}'.format(rec['kobo_id']),
                    'household_member_id_doc_id':u'{}'.format(rec['household_member_id_doc_id']),
                    'household_member_id_doc_type':u'{}'.format(rec['household_member_id_doc_type']),
                    'household_member_id_doc_type_other':u'{}'.format(rec['household_member_id_doc_type_other']),
                    'household_member_id_doc_number':u'{}'.format(rec['household_member_id_doc_number']),
                    'household_member_id':u'{}'.format(rec['household_member_id'])
                }
            )
    return result_as_array

def find_respondent_id_doc_file(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS respondent_doc_sdoc_id'\
                    ', {} AS respondent_doc_id'\
                    ', {} AS respondent_doc_type'\
                    ', {} AS sdoc_id'\
                    ', {} AS sdoc_hname'\
                    ', {} AS sdoc_size'\
                    ', {} AS sdoc_filename'\
                    ', {} AS sdoc_fileext'\
                    ' FROM {}{}'.format(
                        'hl_respondent_document_supporting_document.id', 
                        'hl_respondent_document_supporting_document.respondent_document_id', 
                        'hl_check_respondent_document_document_type.value', 
                        'hl_respondent_document_supporting_document.supporting_doc_id', 
                        'hl_supporting_document.document_identifier', 
                        'hl_supporting_document.document_size', 
                        'hl_supporting_document.filename', 
                        'substring(hl_supporting_document.filename from ' + u"'\..*'" + ')', 
                                               
                        'hl_respondent_document_supporting_document'\
                        ' LEFT JOIN hl_supporting_document ON hl_respondent_document_supporting_document.supporting_doc_id = hl_supporting_document.id'\
                        ' LEFT JOIN hl_check_respondent_document_document_type ON hl_respondent_document_supporting_document.document_type = hl_check_respondent_document_document_type.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'respondent_doc_sdoc_id':u'{}'.format(rec['respondent_doc_sdoc_id']),
                    'respondent_doc_id':u'{}'.format(rec['respondent_doc_id']),
                    'respondent_doc_type':u'{}'.format(rec['respondent_doc_type']),
                    'sdoc_id':u'{}'.format(rec['sdoc_id']),
                    'sdoc_hname':u'{}'.format(rec['sdoc_hname']),
                    'sdoc_size':u'{}'.format(rec['sdoc_size']),
                    'sdoc_filename':u'{}'.format(rec['sdoc_filename']),
                    'sdoc_fileext':u'{}'.format(rec['sdoc_fileext'])
                }
            )
    return result_as_array

def find_evidence_file(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS evidence_sdoc_id'\
                    ', {} AS evidence_id'\
                    ', {} AS evidence_doc_type'\
                    ', {} AS sdoc_id'\
                    ', {} AS sdoc_hname'\
                    ', {} AS sdoc_size'\
                    ', {} AS sdoc_filename'\
                    ', {} AS sdoc_fileext'\
                    ' FROM {}{}'.format(
                        'hl_evidence_supporting_document.id', 
                        'hl_evidence_supporting_document.evidence_id', 
                        'hl_check_evidence_document_type.value', 
                        'hl_evidence_supporting_document.supporting_doc_id', 
                        'hl_supporting_document.document_identifier', 
                        'hl_supporting_document.document_size', 
                        'hl_supporting_document.filename', 
                        'substring(hl_supporting_document.filename from ' + u"'\..*'" + ')', 
                                               
                        'hl_evidence_supporting_document'\
                        ' LEFT JOIN hl_check_evidence_document_type ON hl_evidence_supporting_document.document_type = hl_check_evidence_document_type.id'\
                        ' LEFT JOIN hl_supporting_document ON hl_evidence_supporting_document.supporting_doc_id = hl_supporting_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'evidence_sdoc_id':u'{}'.format(rec['evidence_sdoc_id']),
                    'evidence_id':u'{}'.format(rec['evidence_id']),
                    'evidence_doc_type':u'{}'.format(rec['evidence_doc_type']),
                    'sdoc_id':u'{}'.format(rec['sdoc_id']),
                    'sdoc_hname':u'{}'.format(rec['sdoc_hname']),
                    'sdoc_size':u'{}'.format(rec['sdoc_size']),
                    'sdoc_filename':u'{}'.format(rec['sdoc_filename']),
                    'sdoc_fileext':u'{}'.format(rec['sdoc_fileext'])
                }
            )
    return result_as_array

def find_household_member_id_doc_file(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS household_member_doc_sdoc_id'\
                    ', {} AS household_member_doc_id'\
                    ', {} AS household_member_doc_type'\
                    ', {} AS sdoc_id'\
                    ', {} AS sdoc_hname'\
                    ', {} AS sdoc_size'\
                    ', {} AS sdoc_filename'\
                    ', {} AS sdoc_fileext'\
                    ' FROM {}{}'.format(
                        'hl_household_member_document_supporting_document.id', 
                        'hl_household_member_document_supporting_document.household_member_document_id', 
                        'hl_check_household_member_document_document_type.value', 
                        'hl_household_member_document_supporting_document.supporting_doc_id', 
                        'hl_supporting_document.document_identifier', 
                        'hl_supporting_document.document_size', 
                        'hl_supporting_document.filename', 
                        'substring(hl_supporting_document.filename from ' + u"'\..*'" + ')', 
                                               
                        'hl_household_member_document_supporting_document'\
                        ' LEFT JOIN hl_check_household_member_document_document_type ON hl_household_member_document_supporting_document.household_member_document_id = hl_check_household_member_document_document_type.id'\
                        ' LEFT JOIN hl_supporting_document ON hl_household_member_document_supporting_document.supporting_doc_id = hl_supporting_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'household_member_doc_sdoc_id':u'{}'.format(rec['household_member_doc_sdoc_id']),
                    'household_member_doc_id':u'{}'.format(rec['household_member_doc_id']),
                    'household_member_doc_type':u'{}'.format(rec['household_member_doc_type']),
                    'sdoc_id':u'{}'.format(rec['sdoc_id']),
                    'sdoc_hname':u'{}'.format(rec['sdoc_hname']),
                    'sdoc_size':u'{}'.format(rec['sdoc_size']),
                    'sdoc_filename':u'{}'.format(rec['sdoc_filename']),
                    'sdoc_fileext':u'{}'.format(rec['sdoc_fileext'])
                }
            )
    return result_as_array

def find_respondent_sdocs(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS respondent_sdoc_id'\
                    ', {} AS respondent_id'\
                    ', {} AS respondent_sdoc_type'\
                    ', {} AS sdoc_id'\
                    ', {} AS sdoc_hname'\
                    ', {} AS sdoc_size'\
                    ', {} AS sdoc_filename'\
                    ', {} AS sdoc_fileext'\
                    ' FROM {}{}'.format(
                        'hl_respondent_supporting_document.id', 
                        'hl_respondent_supporting_document.respondent_id', 
                        'hl_check_respondent_document_type.value', 
                        'hl_respondent_supporting_document.supporting_doc_id', 
                        'hl_supporting_document.document_identifier', 
                        'hl_supporting_document.document_size', 
                        'hl_supporting_document.filename', 
                        'substring(hl_supporting_document.filename from ' + u"'\..*'" + ')', 
                                               
                        'hl_respondent_supporting_document'\
                        ' LEFT JOIN hl_check_respondent_document_type ON hl_respondent_supporting_document.document_type = hl_check_respondent_document_type.id'\
                        ' LEFT JOIN hl_supporting_document ON hl_respondent_supporting_document.supporting_doc_id = hl_supporting_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'respondent_sdoc_id':u'{}'.format(rec['respondent_sdoc_id']),
                    'respondent_id':u'{}'.format(rec['respondent_id']),
                    'respondent_sdoc_type':u'{}'.format(rec['respondent_sdoc_type']),
                    'sdoc_id':u'{}'.format(rec['sdoc_id']),
                    'sdoc_hname':u'{}'.format(rec['sdoc_hname']),
                    'sdoc_size':u'{}'.format(rec['sdoc_size']),
                    'sdoc_filename':u'{}'.format(rec['sdoc_filename']),
                    'sdoc_fileext':u'{}'.format(rec['sdoc_fileext'])
                }
            )
    return result_as_array

def find_claim_sdocs(whereclause):
    wrclause = ' {};'.format(whereclause)
    sql_command =   'SELECT '\
                    '  {} AS property_sdoc_id'\
                    ', {} AS property_id'\
                    ', {} AS property_sdoc_type'\
                    ', {} AS sdoc_id'\
                    ', {} AS sdoc_hname'\
                    ', {} AS sdoc_size'\
                    ', {} AS sdoc_filename'\
                    ', {} AS sdoc_fileext'\
                    ' FROM {}{}'.format(
                        'hl_property_supporting_document.id', 
                        'hl_property_supporting_document.property_id', 
                        'hl_check_property_document_type.value', 
                        'hl_property_supporting_document.supporting_doc_id', 
                        'hl_supporting_document.document_identifier', 
                        'hl_supporting_document.document_size', 
                        'hl_supporting_document.filename', 
                        'substring(hl_supporting_document.filename from ' + u"'\..*'" + ')', 
                                               
                        'hl_property_supporting_document'\
                        ' LEFT JOIN hl_check_property_document_type ON hl_property_supporting_document.document_type = hl_check_property_document_type.id'\
                        ' LEFT JOIN hl_supporting_document ON hl_property_supporting_document.supporting_doc_id = hl_supporting_document.id',
                        wrclause
                    )
    result_as_array = []
    result_dataset = fetch_with_filter(sql_command)
    if not result_dataset is None:
        for rec in result_dataset:
            result_as_array.append(
                {
                    'property_sdoc_id':u'{}'.format(rec['property_sdoc_id']),
                    'property_id':u'{}'.format(rec['property_id']),
                    'property_sdoc_type':u'{}'.format(rec['property_sdoc_type']),
                    'sdoc_id':u'{}'.format(rec['sdoc_id']),
                    'sdoc_hname':u'{}'.format(rec['sdoc_hname']),
                    'sdoc_size':u'{}'.format(rec['sdoc_size']),
                    'sdoc_filename':u'{}'.format(rec['sdoc_filename']),
                    'sdoc_fileext':u'{}'.format(rec['sdoc_fileext'])
                }
            )
    return result_as_array

def get_kobo_certificate_filename():
    reg_config = RegistryConfig()
    mapfile = reg_config.read([IMPORT_MAPFILE])
    import_mapfile = mapfile.get(IMPORT_MAPFILE, '')
    certificate_path = os.path.dirname(import_mapfile)
    certificate_file = certificate_path + '\\' + 'kobo_certificate.htm'
    return certificate_file

def get_kobo_certificate_logoimage():
    reg_config = RegistryConfig()
    mapfile = reg_config.read([IMPORT_MAPFILE])
    import_mapfile = mapfile.get(IMPORT_MAPFILE, '')
    logo_path = os.path.dirname(import_mapfile)
    logo_image = logo_path + '\\' + 'logo.png'
    return logo_image

def get_param_index(lines, prm):
    txt = '<p id=p_value>${}</p>'.format(prm)           
    print('PRM:  ', prm)
    print(lines)
    return lines.index(txt)

def get_image_index(lines, img):
    txt = '<img id=p_value src=${}>'.format(img)           
    return lines.index(txt)

def get_loop_start_index(lines,loopname):
    txt = '<p id=loop>[{}_start]</p>'.format(loopname)
    return lines.index(txt)

def get_loop_end_index(lines,loopname):
    txt = '<p id=loop>[{}_end]</p>'.format(loopname)
    return lines.index(txt)

def get_looplines(lines, loopname):
    loop_start = get_loop_start_index(lines,loopname)
    loop_end = get_loop_end_index(lines, loopname)
    return lines[loop_start + 1:loop_end]

def replace_loop_slice(lines, loopname, looplines):
    if len(lines) == 0:
        return [] 
    newlines = lines[:get_loop_start_index(lines,loopname) ]
    newlines += looplines
    newlines += lines[get_loop_end_index(lines,loopname) +1: len(lines)]
    return newlines

def kobo_certificate_setlanguage(cert_lang):
    en_cert_template = get_kobo_certificate_filename().replace('kobo_certificate.htm','kobo_certificate_en.htm')
    ar_cert_template = get_kobo_certificate_filename().replace('kobo_certificate.htm','kobo_certificate_ar.htm')
    cert_template = get_kobo_certificate_filename()

    if 'EN' == cert_lang:
        if not os.path.exists(en_cert_template):
            return False
        shutil.copy(en_cert_template, cert_template)
        return True
    else:
        if not os.path.exists(ar_cert_template):
            return False
        shutil.copy(ar_cert_template, cert_template)
        return True
        
    return False

def kobo_certificate_read_from_template():
    lines = []
    lang = 'EN'
    with io.open(get_kobo_certificate_filename(),'r',encoding='utf-8') as f:
        for line in f:
            unicode_line = u'{}'.format(line.strip())
            if lang == 'EN':
                if 'lang="ar"' in unicode_line:
                    lang = 'AR'
            lines.append(unicode_line)

    return lines, lang
    
def kobo_certificate_save_to_file(lines, filename):
    dest_path = os.path.dirname(filename)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    with io.open(filename, 'w', encoding='utf-8', newline='\n') as html_file:
        for line in lines:
            try:
                html_file.write(u'{}\n'.format(line))
            except:
                ErrMessage(line)    
    return

def update_param(lines, prm, val):
    if len(lines) == 0:
        return
    indx = get_param_index(lines, prm)
    #ErrMessage(lines[indx])
    if val is None:
        val = 'None'
    if '' == val.strip():
        val = 'None'
    if 'none' != val.lower():
        txt = val
        lines[indx] = u'<p id=p_value>{}</p>'.format(txt)
    else:
        if (False == prm.endswith('_other')) and  (prm != 'consent_refuse_reason'):
            lines[indx] = u'<p id=p_value><></p>'
        else:
            lines[indx] = u'<p id=p_value></p>' 
    #ErrMessage(lines[indx])
    return

def update_line(lines, indx, newline):
    if len(lines) == 0:
        return
    if ('' == newline):
        lines[indx] = ''
    else:
        lines[indx] = u'{}'.format(newline)
    return

def update_image(lines, img, val, alt):
    if len(lines) == 0:
        return
    indx = get_image_index(lines, img)
    #ErrMessage(lines[indx])
    img_id = ''
    if img == 'signature_img':
        img_id = u'{}'.format('id=img_signature')
    txt = val
    if alt == '':
        lines[indx] =  u'<p id=p_value>{}</p>'.format('')
        return
    
    lines[indx] = u'<img {} src="{}" alt="{}">'.format(img_id, txt, alt)
    
    #ErrMessage(lines[indx])
    return

def make_supporting_doc(doc_name, source_entity):
    doc_size = os.path.getsize(doc_name)
    path, filename = os.path.split(str(doc_name))
    ht = hashlib.sha1(filename.encode('utf-8'))
    document = {}

    document['support_doc_table'] = 'hl_supporting_document'
    document['creation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    document['hashed_filename'] = ht.hexdigest()
    document['source_entity'] = source_entity
    document['doc_filename'] = filename
    document['document_size'] = doc_size

    return document

def copy_new_support_doc_file(old_file, new_filename, doc_type, entity_name):
    reg_config = RegistryConfig()
    support_doc_path = reg_config.read([NETWORK_DOC_RESOURCE])
    
    old_file_type = 1

    path, filename = os.path.split(str(old_file))
    name, file_ext = os.path.splitext(filename)

    doc_path = support_doc_path.values()[0]
    
    curr_profile = current_profile()
    profile_name = curr_profile.name

    entity_name = entity_name
    doc_type = doc_type.replace(' ', '_').lower()

    dest_path = (doc_path
                    + '/' + profile_name.lower()
                    + '/' + entity_name
                    + '/' + doc_type
                    + '/'
                    )
    dest_filename = dest_path + new_filename + file_ext
    try:
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        shutil.copy(old_file, dest_filename)
        return True
    except:
        return False

def get_filename_from_stdm(entity, type, name, ext):
    reg_config = RegistryConfig()
    support_doc_path = reg_config.read([NETWORK_DOC_RESOURCE])
    doc_path = support_doc_path.values()[0]
    profile_name = current_profile().name
    doc_type = type.replace(' ', '_').lower()
    path =  '{}/{}/{}/{}/'.format (
        doc_path,
        profile_name.lower(),
        entity,
        doc_type
    )
    result = '{}{}{}'.format(path, name, ext)
    if not os.path.exists(result):
        result = ''
    return result

def add_enumeration_supporting_document(enum_id, file_fullname):
    fix_auto_sequences('hl_enumeration_supporting_document', 'id')
    fix_auto_sequences('hl_supporting_document', 'id')

    entity_name = 'hl_enumeration'
    support_doc = make_supporting_doc(file_fullname, entity_name)
    result = pg_create_supporting_document(support_doc)
    if result is None:
        return
        
    dataset_column_ref_name = entity_name.replace('hl_','')
    dataset_column_ref_name += '_id'

    next_support_doc_id = result.fetchone()[0]
    if next_support_doc_id != None:
        parent_supporting_doc_id = \
            pg_create_parent_supporting_document(
               'hl_enumeration_supporting_document',
                next_support_doc_id,
                enum_id,
                1,
               dataset_column_ref_name
            )

    # copy file to STDM supporting document folder
    doc_type = 'General'
    new_filename = support_doc['hashed_filename']
                
    copy_new_support_doc_file(
        file_fullname,
        new_filename,
        doc_type,
        entity_name
    )
    return

def add_calim_supporting_document(property_id, file_fullname):
    fix_auto_sequences('hl_property_supporting_document', 'id')
    fix_auto_sequences('hl_supporting_document', 'id')
    fix_auto_sequences('hl_check_property_document_type', 'id')

    doc_type = 'kobo certificate'
    doc_type_id = get_value_by_column(
        'hl_check_property_document_type',
        'id',
        'value',
        "'" + doc_type + "'"
    )

    entity_name = 'hl_property'

    if doc_type_id is None:
       doc_type_id = _execute(
        "INSERT INTO hl_check_property_document_type (value) VALUES ('{}') RETURNING id".format(
           'kobo certificate'
        )
       ) 

    support_doc = make_supporting_doc(file_fullname, entity_name)
    result = pg_create_supporting_document(support_doc)
    if result is None:
        return
        
    next_support_doc_id = result.fetchone()[0]
    if next_support_doc_id != None:
        parent_supporting_doc_id = \
            pg_create_parent_supporting_document(
               'hl_property_supporting_document',
                next_support_doc_id,
                property_id,
                doc_type_id,
               'property_id'
            )

    # copy file to STDM supporting document folder
    doc_type = doc_type.replace(' ', '_').lower()
    new_filename = support_doc['hashed_filename']
                
    copy_new_support_doc_file(
        file_fullname,
        new_filename,
        doc_type,
        entity_name
    )
    return

def enum_enumerators(whereclause, form):
    cert_path = form.output

    cert_lang = 'EN'
    if not form.Certificate_Language is None:
        if form.Certificate_Language:
            cert_lang = 'AR'
    kobo_certificate_setlanguage(cert_lang)
    
    output_claims = '{}\\calims_{}'.format(cert_path, cert_lang.lower())
    output_koboprofiles = '{}\\kobo_profiles_{}'.format(cert_path,cert_lang.lower())
    output_claims_merged = '{}\\merged'.format(output_claims)

    if not os.path.exists(output_claims):
        os.makedirs(output_claims)
    if not os.path.exists(output_claims_merged):
        os.makedirs(output_claims_merged)

    if not os.path.exists(output_koboprofiles):
        os.makedirs(output_koboprofiles)
    logo_image = get_kobo_certificate_logoimage()
    if os.path.exists(logo_image):
        shutil.copy(logo_image, cert_path + '\\logo.png')

    enums = find_enumerator(whereclause)
    count = 0
    for enum in enums:
        #ErrMessage('enum: {}'.format(enum['enumerator_id']))
        count = count + 1
        form.update_progress.emit(0, u'{}.Printing...{}'.format(str(count), enum['kobo_id']))
        
        lines, lang = kobo_certificate_read_from_template()
        if lang == 'EN':
            footer_align = 'right'
        else:
            footer_align = 'left'
        claim_ref_number_title_index = get_param_index(lines, 'CLAIM_REF_NUMBER_TITLE')
        #claim_qrcode_title_index = get_param_index(lines, 'CLAIM_QRCODE')
        claim_qrcode_image_index = get_param_index(lines, 'CLAIM_QRCODE_IMAGE')

        enum_path = '{}\\{}'.format(cert_path, enum['kobo_id'])
        fname = '{}.htm'.format(enum_path)
        pdfname = '{}.pdf'.format(enum_path)
        

        id_doc_path = '{}\\id_doc'.format(enum_path)
        id_doc_image_path = './{}/id_doc/'.format(enum['kobo_id'])
        resp_sdoc_path = '{}\\resp_sdoc'.format(enum_path)
        resp_sdoc_image_path = './{}/resp_sdoc/'.format(enum['kobo_id'])

        togenerate_certificate = not os.path.exists(pdfname) or form.ForceRegenerate 
        
        if not os.path.exists(enum_path):
            os.makedirs(enum_path)
        
        if togenerate_certificate:
            update_param(lines,'enumerator_name', enum['enumerator_name'])
            update_param(lines,'enumeration_date', enum['enumeration_date'])
            update_param(lines,'enumeration_location', enum['enumeration_location'])
            update_param(lines,'enumeration_location_lat', enum['enumeration_location_lat'])
            update_param(lines,'enumeration_location_long', enum['enumeration_location_long'])
            update_param(lines,'enumeration_location_att', enum['enumeration_location_att'])
            update_param(lines,'enumeration_location_acc', enum['enumeration_location_acc'])
            update_param(lines,'consent_approval', enum['consent_approval'])
            update_param(lines,'consent_refuse_reason', enum['consent_refuse_reason'])
            update_param(lines,'consent_refuse_reason_other', enum['consent_refuse_reason_other'])
            update_param(lines,'respondent_gender', enum['respondent_gender'])
            map_location = '<img id=img_map '
            map_location += 'src="https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom=10&size=540x400'.format(enum['enumeration_location_lat'], enum['enumeration_location_long'])
            map_location += '&scale=2&markers=color:red|{},{}&key=AIzaSyC45nWjy5Cafe53JBv6n34fsTHFFqiydh4">'.format(enum['enumeration_location_lat'], enum['enumeration_location_long'])
               
            if ('' == str(enum['enumeration_location_lat'])) or ('' == str(enum['enumeration_location_long'])):
                update_param(lines, 'enumeration_map_latlon', 'None')
            else:
                update_line(lines,get_param_index(lines, 'enumeration_map_latlon'),map_location)
            
            resps = find_respondent(' WHERE hl_respondent.enumeration = {}'.format(enum['enumerator_id']))
            for resp in resps:
                #ErrMessage(u'respondent: {}'.format(resp['respondent_first_name']))
                update_param(lines,'respondent_first_name', resp['respondent_first_name'])
                update_param(lines,'respondent_last_name', resp['respondent_last_name'])
                update_param(lines,'respondent_father_name', resp['respondent_father_name'])
                update_param(lines,'respondent_mother_name', resp['respondent_mother_name'])
                update_param(lines,'respondent_mobile_number', resp['respondent_mobile_number'])
                update_param(lines,'respondent_whatsapp_number', resp['respondent_whatsapp_number'])
                update_param(lines,'respondent_email', resp['respondent_email'])
                update_param(lines,'respondent_gender', resp['respondent_gender'])
                update_param(lines,'respondent_birthdate', resp['respondent_birthdate'])
                update_param(lines,'respondent_address', resp['respondent_address'])

                update_param(lines,'respondent_education', resp['respondent_education'])
                update_param(lines,'respondent_yearofleave', resp['respondent_yearofleave'])
                update_param(lines,'respondent_numberofdisplacements', resp['respondent_numberofdisplacements'])
                
                resps_id_docs = find_respondent_id_doc(' WHERE hl_respondent_document.respondent = {}'.format(resp['respondent_id']))
                loop1_lines = []
                
                id_doc_count = len(resps_id_docs)
                if lang == 'EN':
                    id_doc_desc = '{} Identification Document'.format(id_doc_count)
                    if id_doc_count > 1:
                        id_doc_desc += 's'
                else:
                    id_doc_desc = u'{} {}'.format(id_doc_count, unicode('وثيقة','utf-8'))
                    if id_doc_count > 1:
                        id_doc_desc = u'{} {}'.format(id_doc_count,  unicode('وثائق','utf-8'))

                id_doc_localnum = 1

                update_param(lines,'respondent_id_doc_count', id_doc_desc)
                for resps_id_doc in resps_id_docs:
                    #ErrMessage(u'respondent id doc of type: {}'.format(resps_id_doc['respondent_id_doc_type']))
                    loop1_lines_org = get_looplines(lines,'loop1')

                    update_param(loop1_lines_org,'respondent_id_doc_type', resps_id_doc['respondent_id_doc_type'])
                    update_param(loop1_lines_org,'respondent_id_doc_type_other', resps_id_doc['respondent_id_doc_type_other'])
                    update_param(loop1_lines_org,'respondent_id_doc_number', resps_id_doc['respondent_id_doc_number'])
                    update_param(loop1_lines_org,'respondent_id_doc_date', resps_id_doc['respondent_id_doc_date'])
                    update_param(loop1_lines_org,'respondent_id_doc_front', resps_id_doc['respondent_id_doc_front'])
                    update_param(loop1_lines_org,'respondent_id_doc_back', resps_id_doc['respondent_id_doc_back'])
                    update_image(loop1_lines_org,'respondent_id_doc_front_img', u'{}{}'.format(id_doc_image_path, resps_id_doc['respondent_id_doc_front']), resps_id_doc['respondent_id_doc_front'])
                    update_image(loop1_lines_org,'respondent_id_doc_back_img', u'{}{}'.format(id_doc_image_path, resps_id_doc['respondent_id_doc_back']), resps_id_doc['respondent_id_doc_back'])

                    resp_id_doc_files = find_respondent_id_doc_file(' WHERE hl_respondent_document_supporting_document.respondent_document_id = {}'.format(resps_id_doc['id_doc_id']))
                    for resp_id_doc_file in resp_id_doc_files:
                        if not os.path.exists(id_doc_path):
                            os.makedirs(id_doc_path)
                        src_file = get_filename_from_stdm(
                            'hl_respondent_document',
                            resp_id_doc_file['respondent_doc_type'],
                            resp_id_doc_file['sdoc_hname'],
                            resp_id_doc_file['sdoc_fileext'],
                        )
                        if src_file != '':
                            shutil.copy(src_file, u'{}/{}'.format(id_doc_path, resp_id_doc_file['sdoc_filename']))
                        
                        #ErrMessage(u'respondent id doc file: {} >> {}'.format(resp_id_doc_file['respondent_doc_type'], resp_id_doc_file['sdoc_filename']))    
                    if id_doc_count > 1:
                        if lang == "EN":
                            loop1_lines.append('<p id=q_subtitle1><strong>Respondent Personal Identification Document({})</strong></p>'.format(id_doc_localnum))
                        else:
                            loop1_lines.append(u'<p id=q_subtitle1><strong>{}({})</strong></p>'.format(unicode('وثيقة تعريف الشخصية','utf-8'), id_doc_localnum))
                        id_doc_localnum += 1
                    loop1_lines += loop1_lines_org
                lines = replace_loop_slice(lines, 'loop1', loop1_lines)    

                #resp_sdoc_path = '{}\\resp_sdoc'.format(enum_path)
                #resp_sdoc_image_path = './{}/resp_sdoc/'.format(enum['kobo_id'])
                resp_sdocs = find_respondent_sdocs(' WHERE hl_respondent_supporting_document.respondent_id = {}'.format(resp['respondent_id']))

                loop9_lines = []
                loop10_lines = []
                resp_photo_count = 0
                hh_group_photo_count = 0
                hh_group_photo_desc = '<>'

                for resp_sdoc in resp_sdocs:
                    #ErrMessage(u'respondent sdoc file: {} >> {}'.format(resp_sdoc['respondent_sdoc_type'], resp_sdoc['sdoc_filename']))    
                    if not os.path.exists(resp_sdoc_path):
                        os.makedirs(resp_sdoc_path)
                    src_file = get_filename_from_stdm(
                        'hl_respondent',
                        resp_sdoc['respondent_sdoc_type'],
                        resp_sdoc['sdoc_hname'],
                        resp_sdoc['sdoc_fileext'],
                    )
                    if src_file != '':
                        shutil.copy(src_file, u'{}/{}'.format(resp_sdoc_path, resp_sdoc['sdoc_filename']))
            
                    if 'Respondent Photo' == resp_sdoc['respondent_sdoc_type']:
                        resp_photo_count += 1
                        loop9_lines_org = get_looplines(lines,'loop9')
                        update_param(loop9_lines_org,'respondent_photo', resp_sdoc['sdoc_filename'])
                        update_image(loop9_lines_org,'respondent_photo_img', u'{}{}'.format(resp_sdoc_image_path, resp_sdoc['sdoc_filename']), resp_sdoc['sdoc_filename'])
                        loop9_lines += loop9_lines_org

                    if 'Household Photo' == resp_sdoc['respondent_sdoc_type']:
                        hh_group_photo_count += 1
                        loop10_lines_org = get_looplines(lines,'loop10')
                        update_param(loop10_lines_org,'household_group_photo', resp_sdoc['sdoc_filename'])
                        update_image(loop10_lines_org,'household_group_photo_img', u'{}{}'.format(resp_sdoc_image_path, resp_sdoc['sdoc_filename']), resp_sdoc['sdoc_filename'])
                        loop10_lines += loop10_lines_org

                    """if resp_sdoc['respondent_sdoc_type'] == 'Respondent Photo':
                        update_param(lines, 'respondent_photo', resp_sdoc['sdoc_filename'] )
                    if resp_sdoc['respondent_sdoc_type'] == 'Household Photo':
                        update_param(lines, 'household_group_photo', resp_sdoc['sdoc_filename'] )"""
                    """if resp_sdoc['respondent_sdoc_type'] == 'Signature':
                        update_param(lines, 'signature', resp_sdoc['sdoc_filename'] )"""
                    
                if resp_photo_count == 0:
                    resp_photo_desc = "<>"
                else:
                    if lang == 'EN':
                        resp_photo_desc = '{} Respondent Photo'.format(resp_photo_count)
                        if resp_photo_count > 1:
                            resp_photo_desc += 's'
                    else:
                        resp_photo_desc = u'{} {}'.format(resp_photo_count, unicode('صورة شخصية','utf-8')) 
                            
                if hh_group_photo_count == 0:
                    hh_group_photo_desc = "<>"
                else:
                    if lang == 'EN':
                        hh_group_photo_desc = '{} Household Group Photo'.format(hh_group_photo_count)
                        if hh_group_photo_count > 1:
                            hh_group_photo_desc += 's'
                    else:
                        hh_group_photo_desc = u'{} {}'.format(resp_photo_count, unicode('صورة لأفراد الأسرة', 'utf-8')) 

                    

                update_param(lines, 'respondent_photo_count', resp_photo_desc)
                update_param(lines, 'household_group_photo_count', hh_group_photo_desc)
                lines = replace_loop_slice(lines, 'loop9', loop9_lines)
                lines = replace_loop_slice(lines, 'loop10', loop10_lines)

                household_members = find_household_member(' WHERE hl_household_member.respondent = {}'.format(resp['respondent_id']))

                loop2_lines = []
                hhm_count = len(household_members)
                hhm_desc = '{} Household member'.format(hhm_count)
                if hhm_count > 1:
                    hhm_desc += 's'
                hhm_localnum = 1

                if hhm_count > 0:
                    update_param(lines,'household_member_count', None)
                else:
                    if lang == 'EN':
                        update_param(lines,'household_member_count', 'No household memenbers')
                    else:
                        update_param(lines,'household_member_count', u'{}'.format(unicode('لا يوجد أفراد أسرة','utf-8')))

                for hhm in household_members:
                    #ErrMessage(u'household member: {}>>{}>>{}'.format(hhm['household_member_relation'], hhm['household_member_first_name'], hhm['household_member_right_type']))
                    loop2_lines_org = get_looplines(lines,'loop2')

                    update_param(loop2_lines_org,'household_member_first_name', hhm['household_member_first_name'])
                    update_param(loop2_lines_org,'household_member_last_name', hhm['household_member_last_name'])
                    update_param(loop2_lines_org,'household_member_father_name', hhm['household_member_father_name'])
                    update_param(loop2_lines_org,'household_member_mother_name', hhm['household_member_mother_name'])
                    update_param(loop2_lines_org,'household_member_relation', hhm['household_member_relation'])
                    update_param(loop2_lines_org,'household_member_relation_other', hhm['household_member_relation_other'])
                    update_param(loop2_lines_org,'household_member_education', hhm['household_member_education'])
                    update_param(loop2_lines_org,'household_memebr_birthdate', hhm['household_memebr_birthdate'])
                    update_param(loop2_lines_org,'household_member_gender', hhm['household_member_gender'])
                    update_param(loop2_lines_org,'household_member_right_type', hhm['household_member_right_type'])
                    update_param(loop2_lines_org,'household_member_right_type_other', hhm['household_member_right_type_other'])

                    household_member_id_docs = find_household_member_id_doc(' where hl_household_member_document.household_member = {} and hl_household_member_document.kobo_parent_index = {}'.format(hhm['household_member_id'], hhm['household_member_kobo_index']))
                    
                    loop3_lines = []

                    hhm_id_doc_count = len(household_member_id_docs)
                    if lang == 'EN':
                        hhm_id_doc_desc = '{} Identification document'.format(hhm_id_doc_count)
                        if hhm_id_doc_count > 1:
                            hhm_id_doc_desc += 's'
                    else:
                        hhm_id_doc_desc = u'{} {}'.format(hhm_id_doc_count, unicode('وثيقة','utf-8'))
                        if hhm_id_doc_count > 1:
                           hhm_id_doc_desc = u'{} {}'.format(hhm_id_doc_count, unicode('وثائق','utf-8'))

                    hhm_id_doc_localnum = 1

                    hhm_id_doc_path = '{}\\hhm_id_doc'.format(enum_path)
                    hhm_id_doc_image_path = './{}/hhm_id_doc/'.format(enum['kobo_id'])

                    for hhm_id_doc in household_member_id_docs:
                        #ErrMessage(u'household member id doc of type: {}'.format(hhm_id_doc['household_member_id_doc_type']))

                        loop3_lines_org = get_looplines(loop2_lines_org,'loop3')

                        update_param(loop3_lines_org,'household_member_id_doc_type', hhm_id_doc['household_member_id_doc_type'])
                        update_param(loop3_lines_org,'household_member_id_doc_type_other', hhm_id_doc['household_member_id_doc_type_other'])
                        update_param(loop3_lines_org,'household_member_id_doc_number', hhm_id_doc['household_member_id_doc_number'])
                        
                        hhm_id_doc_files = find_household_member_id_doc_file(' where hl_household_member_document_supporting_document.household_member_document_id = {}'.format(hhm_id_doc['household_member_id_doc_id']))
                        for hhm_id_doc_file in hhm_id_doc_files:
                            #ErrMessage(u'household member id doc file: {} >> {}'.format(hhm_id_doc_file['household_member_doc_type'], hhm_id_doc_file['sdoc_filename']))            
                            if not os.path.exists(hhm_id_doc_path):
                                os.makedirs(hhm_id_doc_path)
                            src_file = get_filename_from_stdm(
                                'hl_household_member_document',
                                hhm_id_doc_file['household_member_doc_type'],
                                hhm_id_doc_file['sdoc_hname'],
                                hhm_id_doc_file['sdoc_fileext'],
                            )
                            if src_file != '':
                                shutil.copy(src_file, u'{}/{}'.format(hhm_id_doc_path, hhm_id_doc_file['sdoc_filename']))

                        if hhm_id_doc_count > 1:
                            if lang == "EN":
                                loop3_lines.append('<p id=q_subtitle1><strong>Respondent Personal id ({})</strong></p>'.format(hhm_id_doc_localnum))
                            else:
                                loop3_lines.append(u'<p id=q_subtitle1><strong>{}({})</strong></p>'.format(unicode('وثيقة تعريف الشخصية','utf-8'), hhm_id_doc_localnum))
                            hhm_id_doc_localnum += 1
                        loop3_lines += loop3_lines_org
                    loop2_lines_org = replace_loop_slice(loop2_lines_org, 'loop3', loop3_lines) 

                    if hhm_count > 1:
                        if lang == "EN":
                            loop2_lines.append('<p id=q_subtitle1><strong>Household Member ({})</strong></p>'.format(hhm_localnum))
                        else:
                            loop2_lines.append(u'<p id=q_subtitle1><strong>{}({})</strong></p>'.format(unicode('أفراد العائلة','utf-8'), hhm_localnum))
                        hhm_localnum += 1
                    loop2_lines += loop2_lines_org
                lines = replace_loop_slice(lines, 'loop2', loop2_lines)
                    
                claims = find_claim(' WHERE hl_property.respondent = {}'.format(resp['respondent_id']))

                loop4_lines = []

                claim_count = len(claims)
                claim_desc = '{} Claim'.format(claim_count)
                if claim_count > 1:
                    claim_desc += 's'
                claim_localnum = 1

                claim_doc_path = '{}\\claim_doc'.format(enum_path)
                claim_doc_image_path = './{}/claim_doc/'.format(enum['kobo_id'])

                #update_param(lines,'property_count', claim_desc)

                for claim in claims:
                    #ErrMessage(u'claim: {} >> {}'.format(claim['property_type'], claim['claim_ref_number']))
                    if lang == 'EN':
                        update_line(lines, claim_ref_number_title_index, '<p>Claim Reference Number: {}</p>'.format(claim['claim_ref_number']))
                    else:
                        update_line(lines, claim_ref_number_title_index, u'<p>{}: {}</p>'.format(
                            unicode('الرقم المتسلسل للادعاء','utf-8'),
                            claim['claim_ref_number'])
                        )
                    
                    #qrcode generator
                    if not os.path.exists(claim_doc_path):
                        os.makedirs(claim_doc_path)
                    qr_imagename = '{}\\{}.png'.format(claim_doc_path, claim['claim_ref_number'])
                    CREATE_NO_WINDOW = 0x08000000
                    process = subprocess.Popen(
                        'C:/wkhtmltopdf/qrencode -s 150 -o {} {}'.format(qr_imagename,  claim['property_qrcode']),
                        stdout=subprocess.PIPE,
                        shell=False,
                        creationflags = CREATE_NO_WINDOW
                    )
                    process.wait()
                    process = None
                    qr_html_image = '<img id=img_QR src="{}/{}.png" alt="">'.format(claim_doc_image_path, claim['claim_ref_number'])
                    #update_line(lines, claim_qrcode_title_index, '<p>{}</p>'.format(claim['property_qrcode']))
                    update_line(lines, claim_qrcode_image_index, qr_html_image)


                    loop4_lines_org = get_looplines(lines,'loop4')
                    update_param(loop4_lines_org,'claim_ref_number', claim['claim_ref_number'])
                    update_param(loop4_lines_org,'location_is_excact', claim['location_is_excact'])
                    update_param(loop4_lines_org,'location', claim['location'])

                    claim_map_coords = claim['location']
                    while claim_map_coords.find('  ') != -1:
                        claim_map_coords = claim_map_coords.replace('  ', ' ')

                    if '' != claim_map_coords:
                        claim_map_coords = claim_map_coords.replace(' ', ',')
                        while claim_map_coords.find(',,') != -1:
                            claim_map_coords = claim_map_coords.replace(',,', ',')
                        vals = claim_map_coords.split(',')
                        if len(vals) != 2:
                            claim_map_coords = ''
                        else:
                            for coord in vals:
                                if not coord.replace('.', '', 1).isnumeric():
                                    claim_map_coords = ''
                                    break

                    claim_map_location = '<img id=img_map '
                    claim_map_location += 'src="https://maps.googleapis.com/maps/api/staticmap?center={}&zoom=17&size=540x400&maptype=satellite'.format(claim_map_coords)
                    claim_map_location += '&scale=2&markers=color:red|{}&key=AIzaSyC45nWjy5Cafe53JBv6n34fsTHFFqiydh4">'.format(claim_map_coords)


                    stdm_mapname_public = u'{}\\maps\\{}.jpg'.format(cert_path, claim['claim_ref_number'] )
                    if os.path.exists(stdm_mapname_public):
                        stdm_mapname =  u'{}\\{}.jpg'.format(claim_doc_path, claim['claim_ref_number'])
                        if not os.path.exists(claim_doc_path):
                            os.makedirs(claim_doc_path)
                        shutil.copy(stdm_mapname_public, stdm_mapname)
                        claim_map_location = '<img id=img_map src="{}/{}.jpg" height="auto" alt="">'.format(claim_doc_image_path, claim['claim_ref_number'])

                    if '' == str(claim_map_coords):
                        update_param(loop4_lines_org, 'property_map_latlon', 'None')
                    else:
                        update_line(loop4_lines_org,get_param_index(loop4_lines_org, 'property_map_latlon'),claim_map_location)

                    update_param(loop4_lines_org,'location_governorate', claim['location_governorate'])
                    update_param(loop4_lines_org,'location_district', claim['location_district'])
                    update_param(loop4_lines_org,'location_district_other', claim['location_district_other'])
                    update_param(loop4_lines_org,'location_subdistrict', claim['location_subdistrict'])
                    update_param(loop4_lines_org,'location_subdistrict_other', claim['locatin_subdistrict_other'])
                    update_param(loop4_lines_org,'location_community', claim['location_community'])
                    update_param(loop4_lines_org,'location_community_other', '')#
                    update_param(loop4_lines_org,'location_fulladdress', claim['location_fulladdress'])
                    update_param(loop4_lines_org,'location_cadastral_map_number', claim['location_cadastral_map_number'])
                    update_param(loop4_lines_org,'property_damage_by_sattelite', claim['property_damage_by_sattelite'])
                    update_param(loop4_lines_org,'property_damage_by_owner', claim['property_damage_by_owner'])
                    update_param(loop4_lines_org,'property_occupation', claim['property_occupation'])
                    update_param(loop4_lines_org,'property_desc', claim['property_desc'])
                    update_param(loop4_lines_org,'property_type', claim['property_type'])
                    update_param(loop4_lines_org,'property_land_use', claim['property_land_use'])
                    update_param(loop4_lines_org,'property_land_use_other', claim['property_land_use_other'])
                    update_param(loop4_lines_org,'property_buiding_type', claim['property_buiding_type'])
                    update_param(loop4_lines_org,'property_building_use', claim['property_buiding_use'])
                    update_param(loop4_lines_org,'claimed_rights_type', claim['claimed_rights_type'])
                    update_param(loop4_lines_org,'claimed_rights_type_other', '')#
                    update_param(loop4_lines_org,'claimed_rights_share', claim['claimed_rights_share'])
                    update_param(loop4_lines_org,'claimed_inheritance', claim['claimed_inheritance'])
                    update_param(loop4_lines_org,'claimed_inheritance_more_info', claim['claimed_inheritance_more_info'])
                    update_param(loop4_lines_org,'general_comment', claim['general_comment'])
                    update_param(loop4_lines_org,'signature', claim['signature'])
                    update_image(loop4_lines_org,'signature_img', '{}{}'.format(claim_doc_image_path, claim['signature']), claim['signature'])
        
                    claim_sdocs = find_claim_sdocs(' WHERE hl_property_supporting_document.property_id = {}'.format(claim['property_id']))
                    stdm_certificate = ''
                    for claim_sdoc in claim_sdocs:
                        #ErrMessage(u'claim sdoc file: {} >> {}'.format(claim_sdoc['property_sdoc_type'], claim_sdoc['sdoc_filename']))        
                        if not os.path.exists(claim_doc_path):
                            os.makedirs(claim_doc_path)
                        src_file = get_filename_from_stdm(
                            'hl_property',
                            claim_sdoc['property_sdoc_type'],
                            claim_sdoc['sdoc_hname'],
                            claim_sdoc['sdoc_fileext'],
                        )
                        if src_file != '':
                            shutil.copy(src_file, u'{}/{}'.format(claim_doc_path, claim_sdoc['sdoc_filename']))
                            if 'Scanned certificate' == claim_sdoc['property_sdoc_type']:
                                stdm_certificate = u'{}/{}'.format(output_claims, claim_sdoc['sdoc_filename'])
                                shutil.copy(src_file, stdm_certificate)

                    lostdocs = find_lostdoc(' WHERE hl_lost_documents.hl_property_id = {}'.format(claim['property_id']))

                    loop6_lines = []

                    lostdoc_count = len(lostdocs)
                    if lang == 'EN':
                        lostdoc_desc = '{} supporting housing, land and property rights document/ evidence'.format(lostdoc_count)
                    else:
                        lostdoc_desc = u'{} {}'.format(lostdoc_count, unicode('دليل / وثيقة اثبات ملكية', 'utf-8'))
                    if lostdoc_count == 0:
                        lostdoc_desc = "None"

                    update_param(loop4_lines_org, 'lost_doc_count', lostdoc_desc)
                    for lostdoc in lostdocs:
                         #ErrMessage(u'lost document of type: {}'.format(lostdoc['lost_doc_type']))
                        loop6_lines_org = get_looplines(loop4_lines_org,'loop6')
                        update_param(loop6_lines_org, 'lost_doc_type', lostdoc['lost_doc_type'])
                        loop6_lines += loop6_lines_org
                    loop4_lines_org = replace_loop_slice(loop4_lines_org, 'loop6', loop6_lines)

                    evidences = find_evidence(' WHERE hl_evidence.kobo_parent_index = {} and hl_evidence.respondent = {}'.format(claim['kobo_index'], resp['respondent_id']))

                    loop5_lines = []

                    evd_doc_count = len(evidences)
                    
                    if lang == 'EN':
                        evd_doc_desc = '{} Supporting housing, land and property rights document/ evidence'.format(evd_doc_count)
                    else:
                        evd_doc_desc = u'{} {}'.format(evd_doc_count, unicode('دليل / وثيقة اثبات ملكية','utf-8'))

                    evd_doc_localnum = 1

                    evd_doc_path = '{}\\evd_doc'.format(enum_path)
                    evd_doc_image_path = './{}/evd_doc/'.format(enum['kobo_id'])

                    update_param(loop4_lines_org, 'evidence_count', evd_doc_desc)
                    for evd in evidences:
                        #ErrMessage(u'evidence: {} >> {}'.format(evd['evidence_type'], evd['evidence_number']))
                        loop5_lines_org = get_looplines(loop4_lines_org,'loop5')

                        update_param(loop5_lines_org,'evidence_type', evd['evidence_type'])
                        update_param(loop5_lines_org,'evidence_type_other', evd['evidence_type_other'])
                        update_param(loop5_lines_org,'evidence_picture_front', evd['evidence_picture_front'])
                        update_param(loop5_lines_org,'evidence_picture_back', evd['evidence_picture_back'])
                        update_param(loop5_lines_org,'evidence_number', evd['evidence_number'])

                        update_image(loop5_lines_org,'evidence_picture_front_img', u'{}{}'.format(evd_doc_image_path, evd['evidence_picture_front']), evd['evidence_picture_front'])
                        update_image(loop5_lines_org,'evidence_picture_back_img', u'{}{}'.format(evd_doc_image_path, evd['evidence_picture_back']), evd['evidence_picture_back'])

                        loop7_lines = []
                        loop8_lines = []
                        audio_evd_count = 0
                        video_evd_count = 0

                        evd_files = find_evidence_file(' WHERE hl_evidence_supporting_document.evidence_id = {}'.format(evd['evidence_id']))
                        for evd_file in evd_files:
                            #ErrMessage(u'evidence sdoc file: {} >> {}'.format(evd_file['evidence_sdoc_type'], evd_file['sdoc_filename']))                
                            if not os.path.exists(evd_doc_path):
                                os.makedirs(evd_doc_path)
                            src_file = get_filename_from_stdm(
                                'hl_evidence',
                                evd_file['evidence_doc_type'],
                                evd_file['sdoc_hname'],
                                evd_file['sdoc_fileext'],
                            )
                            if src_file != '':
                                shutil.copy(src_file, u'{}/{}'.format(evd_doc_path, evd_file['sdoc_filename']))
                            if 'Audio Evidence' == evd_file['evidence_doc_type']:
                                audio_evd_count += 1
                                loop7_lines_org = get_looplines(loop5_lines_org,'loop7')
                                update_param(loop7_lines_org,'evidence_audio', evd_file['sdoc_filename'])
                                loop7_lines += loop7_lines_org

                            if 'Video Evidence' == evd_file['evidence_doc_type']:
                                video_evd_count += 1
                                loop8_lines_org = get_looplines(loop5_lines_org,'loop8')
                                update_param(loop8_lines_org,'evidence_video', evd_file['sdoc_filename'])
                                loop8_lines += loop8_lines_org
                    
                        if evd_doc_count > 1:
                            if lang == "EN":
                                loop5_lines.append('<p id=q_subtitle1><strong>Evidence ({})</strong></p>'.format(evd_doc_localnum))
                            else:
                                loop5_lines.append(u'<p id=q_subtitle1><strong>{}({})</strong></p>'.format(unicode('أفراد العائلة','utf-8'), evd_doc_localnum))
                            evd_doc_localnum += 1

                        if audio_evd_count == 0:
                            audio_evd_desc = "<>"
                        else:
                            if lang == 'EN':
                                audio_evd_desc = '{} Audio Evidence'.format(audio_evd_count)
                                if audio_evd_count > 1:
                                    audio_evd_desc += 's'
                            else:
                                 audio_evd_desc = u'{} {}'.format(audio_evd_count, unicode('دليل صوتي','utf-8'))
                                
                            
                        if video_evd_count == 0:
                            video_evd_desc = "<>"
                        else:
                            if lang == 'EN':
                                video_evd_desc = '{} Video Evidence'.format(video_evd_count)
                                if video_evd_count > 1:
                                    video_evd_desc += 's'
                            else:
                                video_evd_desc = u'{} {}'.format(video_evd_count,unicode('ملف فيديو', 'utf-8')) 

                        update_param(loop5_lines_org, 'evidence_audio_count', audio_evd_desc)
                        update_param(loop5_lines_org, 'evidence_video_count', video_evd_desc)
                        loop5_lines_org = replace_loop_slice(loop5_lines_org, 'loop7', loop7_lines)
                        loop5_lines_org = replace_loop_slice(loop5_lines_org, 'loop8', loop8_lines)
                        loop5_lines += loop5_lines_org
                    loop4_lines_org = replace_loop_slice(loop4_lines_org, 'loop5', loop5_lines)

                    if claim_count > 1:
                        #loop4_lines.append('<p id=q_title><strong>Property ({} as of {} regsitered by respondent) Information</strong></p>'.format(claim_localnum,claim_count))
                        claim_localnum += 1
                    loop4_lines += loop4_lines_org
                    if '' != claim['claim_ref_number']:
                        claims_lines = replace_loop_slice(lines, 'loop4', loop4_lines_org)                
                        #claim_path = '{}\\{}'.format(cert_path, claim['claim_ref_number'])
                        claim_path = '{}\\{}'.format(cert_path, claim['claim_ref_number'])
                        claim_fname = '{}.htm'.format(claim_path)
                        #claim_pdfname = '{}_{}.pdf'.format(claim_path, enum['kobo_id'])
                        claim_pdfname = '{}_{}.pdf'.format(claim_path, 'ClaimProfile')
                        claim_pdfname_merged = '{}_{}.pdf'.format(claim_path, 'ClaimProfile').replace(cert_path, output_claims_merged)
                        kobo_certificate_save_to_file(claims_lines, claim_fname) 
                        CREATE_NO_WINDOW = 0x08000000
                        
                        process = subprocess.Popen(
                            'C:/wkhtmltopdf/bin/wkhtmltopdf --enable-external-links --enable-local-file-access --footer-{} [page]/[topage] {} {}'.format(footer_align, claim_fname, claim_pdfname),
                            stdout=subprocess.PIPE,
                            shell=False,
                            creationflags = CREATE_NO_WINDOW
                        )
                        process.wait()
                        process = None
                        dst_file = claim_pdfname.replace(cert_path, output_claims)
                        if os.path.exists(dst_file):
                            os.remove(dst_file)
                            
                        if not os.path.exists(claim_pdfname):
                            continue

                        shutil.move(claim_pdfname, output_claims)

                        if stdm_certificate != '':
                            CREATE_NO_WINDOW = 0x08000000
                            process = subprocess.Popen(
                                'C:/wkhtmltopdf/PDFtk/bin/pdftk {} {} output {}'.format(dst_file, stdm_certificate, claim_pdfname_merged),
                                stdout=subprocess.PIPE,
                                shell=False,
                                creationflags = CREATE_NO_WINDOW
                            )
                            process.wait()
                            process = None
                        else:
                            if os.path.exists(dst_file):
                                shutil.copy(dst_file, claim_pdfname_merged)
                                
                        add_calim_supporting_document(claim['property_id'], dst_file)

                lines = replace_loop_slice(lines, 'loop4', loop4_lines)

            kobo_certificate_save_to_file(lines, fname) 
            #os.system('C:/wkhtmltopdf/bin/wkhtmltopdf {} {}'.format(fname, pdfname))
            CREATE_NO_WINDOW = 0x08000000
            process = subprocess.Popen(
                'C:/wkhtmltopdf/bin/wkhtmltopdf --enable-external-links --enable-local-file-access --footer-{} [page]/[topage] {} {}'.format(footer_align, fname, pdfname),
                stdout=subprocess.PIPE,
                shell=False,
                creationflags = CREATE_NO_WINDOW
            )
            process.wait()
            process = None

        if os.path.exists(pdfname):
            if togenerate_certificate:
                msg = '...added...({}) claim (s)...Success'.format(claim_count)
            else:
                msg = '...Already Printed' 
            form.update_progress.emit(1, msg)
            if form.UploadCertificate:
                add_enumeration_supporting_document(enum['enumerator_id'], pdfname)
                form.update_progress.emit(2, '...Uploaded')
            
            dst_file = pdfname.replace(cert_path, output_koboprofiles)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(pdfname, output_koboprofiles)
            #pdftk C:\k_cert_en\calims\SY-cd-01_ClaimProfile.pdf C:\k_cert_en\calims\SY-cd-01.pdf output C:\k_cert_en\calims\_result.pdf

        QApplication.processEvents()
        if form.cancelled:
            return
    form.update_progress.emit(0, u'---------------Completed Successfully-------------------')
    return 0

"""def sample():
    enums = find_enumerator(whereclause)
    if len(enums) == 0:
        return 
    for enum in enums:
        resps = find_respondent(' WHERE hl_respondent.kobo_id = {}'.format(enum['kobo_id']))
        for resp in resps:
            hhms = find_household_member(' WHERE hl_household_member.kobo_submission_id = {}'.format(resp['kobo_id']))
            for hhm in hhms:
                pass#ErrMessage(u'{}'.format(hhm['household_member_first_name']))
            claims = find_claim(' WHERE hl_property.respondent = {}'.format(resp['respondent_id']))
            for clm in claims:
                lostdocs = find_evidence(' WHERE hl_evidence.respondent = {}'.format(resp['respondent_id']))
                for evd in evds:
                    pass#ErrMessage(u'{}'.format(evd['evidence_number']))
                
            evds = find_evidence(' WHERE hl_evidence.respondent = {}'.format(resp['respondent_id']))
            for evd in evds:
                pass#ErrMessage(u'{}'.format(evd['evidence_number']))
                
    return"""


def ErrMessage(message):
    #Error Message Box
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.exec_()