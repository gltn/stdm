--Returns a list of views related to a given table
SELECT distinct dependee.relname as view_name
FROM pg_depend 
JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid 
JOIN pg_class as dependee ON pg_rewrite.ev_class = dependee.oid 
JOIN pg_class as dependent ON pg_depend.refobjid = dependent.oid 
JOIN pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid 
    AND pg_depend.refobjsubid = pg_attribute.attnum 
WHERE dependent.relname = :table_name;