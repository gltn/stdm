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
