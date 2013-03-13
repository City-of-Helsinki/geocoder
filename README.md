geocoder
========

Environment installation
------------------------

Ubuntu packages:
    virtualenvwrapper libpq-dev python-dev

Shell commands:
    mkvirtualenv geocoder
    pip install -r requirements.txt

Database installation
---------------------

Ubuntu packages:
    language-pack-fi postgis postgresql postgresql-contrib

Shell commands:pg
    sudo su postgres
    createdb -l fi_FI.UTF8 -E UTF8 -T template0 template_postgis
    # (following can already be installed)
    createlang -d template_postgis plpgsql
    psql -d template_postgis -c"CREATE EXTENSION hstore;"
    psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-2.0/postgis.sql
    psql -d template_postgis -f /usr/share/postgresql/9.1/contrib/postgis-2.0/spatial_ref_sys.sql
    psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
    psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
    psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
    createuser -R -S -D -P geocoder
    createdb -O geocoder -T template_postgis -E utf8 geocoder

Edit file /etc/postgresql/9.1/main/pg_hba.conf. Change line
    local   all             all                                     peer
to
    local   all             all                                     md5

Now, restart the postgres server:
    sudo service postgresql restart
