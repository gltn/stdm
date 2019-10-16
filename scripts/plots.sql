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

--- Delete duplicate plots if any

CREATE OR REPLACE FUNCTION delete_duplicate_plots()
  RETURNS trigger AS
$$
BEGIN
 DELETE FROM cb_plot
 WHERE key IN
    (SELECT key
    FROM
        (SELECT key,
         ROW_NUMBER() OVER( PARTITION BY transactiondate,
         upi,geom
        ORDER BY  key ) AS row_num
        FROM cb_plot ) t
        WHERE t.row_num > 1 );
        RETURN NULL;
        END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER delete_duplicate_plots()
  AFTER INSERT ON cb_plot
  FOR EACH ROW EXECUTE PROCEDURE delete_duplicate_plots();

-- delete rows from staging table

CREATE OR REPLACE FUNCTION clear_staging() RETURNS TRIGGER AS $clear_staging$
    BEGIN
        --- clear rows
        TRUNCATE cb_lis_plot;
        RETURN NULL;
    END;

$clear_staging$ LANGUAGE plpgsql;

CREATE TRIGGER clear_staging
AFTER INSERT ON cb_lis_plot
    FOR EACH ROW EXECUTE PROCEDURE clear_staging();
