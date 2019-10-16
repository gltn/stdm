-- ----------------------------
-- Scheme Log
-- ----------------------------

DROP TABLE IF EXISTS "public"."cb_scheme_log";
CREATE TABLE "public"."cb_scheme_log" (
  "operation" varchar(1),
  "stamp" timestamp(6),
  "user_id" text,
  "id" int4,
  "scheme_name" varchar(50),
  "date_of_approval" date,
  "date_of_establishment" date,
  "relevant_authority" int4,
  "land_rights_office" int4,
  "region" int4,
  "title_deed_number" varchar(30),
  "township_name" varchar(100),
  "registration_division" int4,
  "area" numeric(15,4),
  "doc_imposing_conditions" varchar(30),
  "constitution_ref_no" varchar(30),
  "no_of_plots" int4,
  "scheme_number" varchar(32),
  "scheme_id" int4
)
;

-- ----------------------------
-- Holder Log
-- ----------------------------
DROP TABLE IF EXISTS "public"."cb_holder_log";
CREATE TABLE "public"."cb_holder_log" (
  "operation" varchar(1),
  "stamp" timestamp(6),
  "user_id" text,
  "id" int4,
  "first_name" varchar(50),
  "surname" varchar(50),
  "gender" int4,
  "holder_identifier" varchar(20),
  "date_of_birth" date,
  "name_of_juristic_person" varchar(50),
  "reg_no_of_juristic_person" varchar(50),
  "marital_status" int4,
  "spouse_surname" varchar(50),
  "spouse_first_name" varchar(50),
  "spouse_gender" int4,
  "spouse_identifier" varchar(20),
  "spouse_date_of_birth" date,
  "disability_status" int4,
  "income_level" int4,
  "occupation" int4,
  "other_dependants" int4
)
;

---- SCHEME LOG

CREATE OR REPLACE FUNCTION cb_scheme_log() RETURNS TRIGGER AS $cb_scheme_log$
    BEGIN
        --
        -- Create a row in lht_approval_log to reflect the operation performed on cb_scheme,
        -- make use of the special variable TG_OP to work out the operation.
        --
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO cb_scheme_log SELECT 'D', now(), user, OLD.*;
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO cb_scheme_log SELECT 'U', now(), user, NEW.*;
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO cb_scheme_log SELECT 'I', now(), user, NEW.*;
            RETURN NEW;
        END IF;
        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
$cb_scheme_log$ LANGUAGE plpgsql;

CREATE TRIGGER cb_scheme_log
AFTER INSERT OR UPDATE OR DELETE ON cb_scheme
    FOR EACH ROW EXECUTE PROCEDURE cb_scheme_log();

---- HOLDER LOG

CREATE OR REPLACE FUNCTION cb_holder_log() RETURNS TRIGGER AS $cb_holder_log$
    BEGIN
        --
        -- Create a row in lht_approval_log to reflect the operation performed on cb_holder,
        -- make use of the special variable TG_OP to work out the operation.
        --
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO cb_holder_log SELECT 'D', now(), user, OLD.*;
            RETURN OLD;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO cb_holder_log SELECT 'U', now(), user, NEW.*;
            RETURN NEW;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO cb_holder_log SELECT 'I', now(), user, NEW.*;
            RETURN NEW;
        END IF;
        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
$cb_holder_log$ LANGUAGE plpgsql;

CREATE TRIGGER cb_holder_log
AFTER INSERT OR UPDATE OR DELETE ON cb_holder
    FOR EACH ROW EXECUTE PROCEDURE cb_holder_log();

---- UPDATE PLOTS FROM STAGING TABLE

CREATE OR REPLACE FUNCTION insert_plots() RETURNS TRIGGER AS $insert_plots$
    BEGIN
        --- Update plot from lis_plot
        INSERT INTO cb_plot (geom, upi, use)
	    SELECT
	    t.geom, t.upi, u."id"
	    FROM
	    cb_lis_plot t
	    INNER JOIN cb_check_lht_plot_use u ON u."value" = t.use
	    WHERE t.geom NOT IN (select geom from cb_plot);
        RETURN NULL;
    END;

$insert_plots$ LANGUAGE plpgsql;

CREATE TRIGGER insert_plots
AFTER INSERT ON cb_lis_plot
    FOR EACH ROW EXECUTE PROCEDURE insert_plots();
