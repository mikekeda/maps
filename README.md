Maps
======================

This is site where you can build statistic interactive webmaps.

Installation
------------
    # Install gdal
    sudo apt-get install gdal-bin
    # Install Redis
    sudo apt install redis-server
    # Install postgresql
    sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main"
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get install postgresql-9.6
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
