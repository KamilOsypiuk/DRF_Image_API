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
## Setup

Note: Command make build should create .env file in root directory but in case if this file is not created, create .env file manually, copy .env.template to it and set your own variables.

1. Clone repository: `$ git clone https://github.com/KamilOsypiuk/DRF_Image_API/`
2. Run in root directory: `$ make build`
3. Run project: `$ make up`

## Fixtures
`$ make fixtures`

## Migrations
`$ make migrations`

## Tests
`$ make test`

## Create admin
`$ make superuser`

After that you should be able to work with browsable API through http://127.0.0.1:8000/ url and log in as admin through http://127.0.0.1:8000/admin/login/?next=/admin/



