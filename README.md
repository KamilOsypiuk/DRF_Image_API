# DRF_Image_API

DRF API allowing to upload Images based on three built-in tiers, backed with PostgreSQL database and celery library for background tasks

# TECH STACK
- Python 3.10
- Django 4.2.6
- Django Rest Framework 3.14
- PostgreSQL

# Functionalities
- Login done with dj_rest_auth and restframework_simplejwt, due to skipped registration users are created via django admin panel
- User are assigned to three built-in tier like Basic, Premium or Enterprise.
- Except from built-in tiers admins are able to create custom tier through admin panel with arbitrary thumbnail sizes,
  access to original link and ability to create expiration links attributes
- User based on their tiers can perform specific actions on Images

# Project setup
Note: As for now project doesn't use Docker therefore it's needed to install external technologies like PostgreSQL, Redis server and Python.

After installing external tech and setting up database you can follow this steps in python terminal:
  1. pip install -r requirements.txt
  2. python manage.py loaddata fixtures/fixtures.json  
  3. python manage.py createsuperuser
  4. python manage.py makemigrations
  5. python manage.py migrate
  6. python manage.py runserver and celery -A api worker -l info in two seprate python terminals
  7. Additionally: python manage.py test

After that you should be able to work with API through http://127.0.0.1:8000/ url and log in as admin through http://127.0.0.1:8000/admin/login/?next=/admin/



