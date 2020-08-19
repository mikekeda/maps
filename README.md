Maps
======================

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a1e8f75dac9462aafa4803e9cfc5fdc)](https://app.codacy.com/manual/mikekeda/maps?utm_source=github.com&utm_medium=referral&utm_content=mikekeda/maps&utm_campaign=Badge_Grade_Dashboard)

Site where you can build statistic interactive webmaps.
Link to the site - <https://maps.mkeda.me>

Installation
------------
    # Install gdal
    sudo apt-get install gdal-bin
    # Install Redis
    sudo apt install redis-server
    # Install postgresql
    echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-12
    # Configure database
    sudo su - postgres
    psql
    CREATE USER maps_admin WITH PASSWORD 'home_pass';
    CREATE DATABASE maps;
    GRANT ALL PRIVILEGES ON DATABASE maps to maps_admin;
    # Install packages
    pip install -r requirements.txt
    # Apply migrations
    python manage.py migrate
    # Create an admin user
    python manage.py createsuperuser
    # Import Polygons from geojson files
    python manage.py import

Running
-------
    # Locally
    python manage.py runserver

Upgrade python packages
-------
    # Remove versions from requirements.txt
    # Upgrade python packages
    pip install --upgrade --force-reinstall -r requirements.txt
    # Update requirements.txt
    pip freeze > requirements.txt
