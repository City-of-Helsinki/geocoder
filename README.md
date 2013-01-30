Database installation
---------------------

Shell commands:
    sudo su postgres
    createdb -l fi_FI.UTF8 -E UTF8 -T template0 template_postgis
    # (following can already be installed)
    createlang -d template_postgis plpgsql
    psql -d template_postgis -c"CREATE EXTENSION hstore;"
    psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
    psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
    psql -d template_postgis -c "select postgis_lib_version();"
    psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
    psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
    createuser -D -P geocoder
    createdb -O geocoder -T template_postgis -E utf8 geocoder
