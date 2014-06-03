from sqlalchemy import *
from sqlalchemy import create_engine, MetaData

from sqlalchemy import Column, Date, Integer, String ,Numeric,Text,Boolean
from qtalchemy import UserAttr
from sqlalchemy.orm import relationship, backref
import datetime


class party(object):
	id=UserAttr(int,'id')
	address=UserAttr(str,'address')
	contact=UserAttr(int,'contact')
	Identity=UserAttr(int,'Identity')

class person(object):
	id=UserAttr(int,'id')
	first_name=UserAttr(str,'first_name')
	last_name=UserAttr(str,'last_name')
	age=UserAttr(int,'age')
	contact=UserAttr(int,'contact')
	education_level=UserAttr(str,'education_level')
	houshold=UserAttr(str,'houshold')
	work=UserAttr(str,'work')
	marital_status=UserAttr(str,'marital_status')
	birth_date=UserAttr(datetime.date,'date')
	pguid=relationship('party',backref='person')

class household(object):
	id=UserAttr(int,'id')
	previous_resdence=UserAttr(str,'previous_resdence')
	settlement_period=UserAttr(str,'settlement_period')
	hguid=relationship('party',backref='household')

class services(object):
	name=UserAttr(str,'name')
	source=UserAttr(str,'source')
	id=UserAttr(int,'id')

class project_area(object):
	id=UserAttr(int,'id')
	name=UserAttr(str,'name')
	location=UserAttr(str,'location')
	code=UserAttr(int,'code')

class respondent(object):
	id=UserAttr(int,'id')
	first_name=UserAttr(str,'first_name')
	last_name=UserAttr(str,'last_name')
	relationship=UserAttr(str,'relationship')

class property(object):
	id=UserAttr(int,'id')

class spatial_unit(object):
	id=UserAttr(int,'id')
	unit_name=UserAttr(str,'unit_name')
	use_of_the_unit=UserAttr(str,'use_of_the_unit')
	registration_date=UserAttr(datetime.date,'date')

class source_document(object):
	id=UserAttr(int,'id')
	type=UserAttr(str,'type')
	person_id=UserAttr(int,'person_id')
	household_id=UserAttr(int,'household_id')

class check_gender(object):
	value=UserAttr(str,'value')

class check_use_type(object):
	value=UserAttr(str,'value')
	value=UserAttr(str,'value')
