CREATE TABLE party (
	id integer,
	address character varying( 80) NOT NULL,
	contact integer,
	identity integer,
	CONSTRAINT pk_party PRIMARY KEY (id));
CREATE TABLE person (
	id serial NOT NULL,
	first_name character varying( 80),
	last_name character varying( 80),
	age integer,
	contact integer,
	education_level character varying( 45),
	houshold character varying( 50),
	work character varying( 60),
	marital_status character varying( 50),
	birth_date date( 50),
	CONSTRAINT pk_person PRIMARY KEY (id));
ALTER TABLE person ADD CONSTRAINT pguid FOREIGN KEY (id) REFERENCES party(id) ON DELETE CASCADE ON UPDATE CASCADE;
CREATE TABLE household (
	id integer,
	previous_resdence character varying( 100),
	settlement_period character varying( 50),
	CONSTRAINT pk_household PRIMARY KEY (id));
ALTER TABLE household ADD CONSTRAINT hguid FOREIGN KEY (id) REFERENCES party(id) ON DELETE CASCADE ON UPDATE CASCADE;
CREATE TABLE services (
	name character varying( 45),
	source character varying( 10),
	id integer
);
CREATE TABLE project_area (
	id integer,
	name character varying( 50),
	location character varying( 50),
	code integer
);
CREATE TABLE respondent (
	id integer,
	first_name character varying( 50),
	last_name character varying( 50),
	relationship character varying( 40),
	CONSTRAINT pk_respondent PRIMARY KEY (id));
ALTER TABLE respondent ADD CONSTRAINT houseid FOREIGN KEY (id) REFERENCES household(id) ON DELETE CASCADE ON UPDATE CASCADE;
CREATE TABLE property (
	id integer,
	name character varying( 30),
	value character varying( 10),
	tax real
);
ALTER TABLE property ADD CONSTRAINT spguuid FOREIGN KEY (id) REFERENCES spatial_unit(id) ON DELETE CASCADE ON UPDATE CASCADE;
CREATE TABLE spatial_unit (
	id integer,
	unit_name character varying( 25),
	use_of_the_unit character varying( 25),
	registration_date date,
	CONSTRAINT pk_spatial_unit PRIMARY KEY (id));
CREATE TABLE source_document (
	id integer,
	type character varying( 25),
	person_id integer,
	household_id integer,
	CONSTRAINT pk_source_document PRIMARY KEY (id,
	household_id));
CREATE TABLE social_tenure (
	id integer,
	social_tenure_type character varying( 50),
	person_id integer,
	spatial_unit_id integer,
	group_id integer,
	share integer,
	CONSTRAINT pk_social_tenure PRIMARY KEY (id));
CREATE TABLE social_tenure (
	id integer,
	social_tenure_type character varying( 50),
	person_id integer,
	spatial_unit_id integer,
	group_id integer,
	share integer,
	CONSTRAINT pk_social_tenure PRIMARY KEY (id));
CREATE TABLE check_gender (
	value character varying( 50)
);
CREATE TABLE check_use_type (
	value character varying( 50),
	value character varying( 50)
);
