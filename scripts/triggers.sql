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