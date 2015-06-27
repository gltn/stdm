CREATE TABLE check_document_type (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_document_type PRIMARY KEY (id));
CREATE TABLE check_social_tenure_type (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_social_tenure_type PRIMARY KEY (id));
CREATE TABLE check_previous_residence (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_previous_residence PRIMARY KEY (id));
CREATE TABLE check_gender (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_gender PRIMARY KEY (id));
CREATE TABLE check_settlement_reason (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_settlement_reason PRIMARY KEY (id));
CREATE TABLE check_montly_income (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_montly_income PRIMARY KEY (id));
CREATE TABLE check_rent (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_rent PRIMARY KEY (id));
CREATE TABLE check_type (
	id serial,
	value character varying( 50),
	CONSTRAINT pk_check_type PRIMARY KEY (id));
CREATE TABLE party (
	id serial,
	family_name character varying( 25),
	other_names character varying( 25),
	address character varying( 25),
	identification integer,
	contact_telephone character varying( 25),
	age integer,
	gender character varying( 25),
	date_of_birth date,
	CONSTRAINT pk_party PRIMARY KEY (id));
CREATE TABLE spatial_unit (
	id serial,
	spatial_unit_id character varying( 25),
	name character varying( 25),
	type character varying( 25),
	sp_unit_use character varying( 50),
	CONSTRAINT pk_spatial_unit PRIMARY KEY (id));
CREATE TABLE supporting_document (
	id serial,
	document_type character varying( 25),
	date_of_recording date,
	validity character varying( 50),
	source character varying( 50),
	document_id character varying( 50),
	filename character varying( 50),
	party serial,
	CONSTRAINT pk_supporting_document PRIMARY KEY (id));
CREATE TABLE social_tenure_relationship (
	id serial,
	social_tenure_type character varying( 25),
	share double precision,
	party integer,
	spatial_unit integer,
	CONSTRAINT pk_social_tenure_relationship PRIMARY KEY (id));
CREATE TABLE household (
	id serial,
	total_persons integer,
	rent character varying( 50),
	reason_for_settlement character varying( 50),
	previous_stay character varying( 50),
	income character varying( 50),
	CONSTRAINT pk_household PRIMARY KEY (id));
SELECT AddGeometryColumn('spatial_unit', 'geom_line', '4326','LINESTRING',2);
SELECT AddGeometryColumn('spatial_unit', 'geom_polygon', '4326','POLYGON',2);
SELECT AddGeometryColumn('spatial_unit', 'geom_point', '4326','POINT',2);
SELECT AddGeometryColumn('spatial_unit', 'structures', '4326','POLYGON',2);
ALTER TABLE supporting_document ADD CONSTRAINT psd FOREIGN KEY (party) REFERENCES party(id) ON DELETE SET NULL ON UPDATE SET NULL;
ALTER TABLE social_tenure_relationship ADD CONSTRAINT pid1 FOREIGN KEY (spatial_unit) REFERENCES spatial_unit(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE social_tenure_relationship ADD CONSTRAINT partyid FOREIGN KEY (party) REFERENCES party(id) ON DELETE CASCADE ON UPDATE CASCADE;
INSERT INTO check_document_type ("value") VALUES ('Audio Files');
INSERT INTO check_document_type ("value") VALUES ('Video Files');
INSERT INTO check_document_type ("value") VALUES ('Rent certificate');
INSERT INTO check_document_type ("value") VALUES ('Lease agreement');
INSERT INTO check_document_type ("value") VALUES ('Title');
INSERT INTO check_social_tenure_type ("value") VALUES ('Tenant');
INSERT INTO check_social_tenure_type ("value") VALUES ('Individual owner');
INSERT INTO check_social_tenure_type ("value") VALUES ('Part owner/shared ownership');
INSERT INTO check_social_tenure_type ("value") VALUES ('Lease');
INSERT INTO check_social_tenure_type ("value") VALUES ('Occupant');
INSERT INTO check_social_tenure_type ("value") VALUES ('Others');
INSERT INTO check_previous_residence ("value") VALUES ('Here');
INSERT INTO check_previous_residence ("value") VALUES ('Another town');
INSERT INTO check_previous_residence ("value") VALUES ('Another settlement');
INSERT INTO check_gender ("value") VALUES ('Male');
INSERT INTO check_gender ("value") VALUES ('Female');
INSERT INTO check_settlement_reason ("value") VALUES ('Eviction');
INSERT INTO check_settlement_reason ("value") VALUES ('Poverty');
INSERT INTO check_settlement_reason ("value") VALUES ('Job opportunity');
INSERT INTO check_montly_income ("value") VALUES ('below 1000');
INSERT INTO check_montly_income ("value") VALUES ('1001-2500');
INSERT INTO check_montly_income ("value") VALUES ('2501-5000');
INSERT INTO check_montly_income ("value") VALUES ('5000-10000');
INSERT INTO check_montly_income ("value") VALUES ('10000-20000');
INSERT INTO check_montly_income ("value") VALUES ('Above 20000');
INSERT INTO check_rent ("value") VALUES ('1000');
INSERT INTO check_rent ("value") VALUES ('3000');
INSERT INTO check_rent ("value") VALUES ('4000');
INSERT INTO check_rent ("value") VALUES ('5000');
INSERT INTO check_type ("value") VALUES ('water');
INSERT INTO check_type ("value") VALUES ('drainage');
CREATE OR REPLACE VIEW social_tenure_relations AS SELECT party.id, party.family_name AS party_surname, party.other_names,         party.identification, spatial_unit.spatial_unit_id AS spatial_unit_number, spatial_unit.name AS spatial_unit_name, spatial_unit.geom_polygon AS geometry,         social_tenure_relationship.social_tenure_type FROM party, spatial_unit, social_tenure_relationship         WHERE spatial_unit.id = social_tenure_relationship.spatial_unit AND party.id = social_tenure_relationship.party; 