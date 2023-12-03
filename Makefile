build:
	-cp -u .env.template .env
	docker-compose build

up:
	docker-compose exec backend bash "python manage.py makemigrations && python manage.py migrate"
	docker-compose exec backend bash -c "python manage.py loaddata fixtures/fixtures.json"
	docker-compose up

fixtures:
	docker-compose exec backend bash -c "python manage.py loaddata fixtures/fixtures.json"

migrations:
	docker-compose exec backend bash -c "python manage.py makemigrations && python manage.py migrate"

superuser:
	docker-compose exec backend bash -c "python manage.py createsuperuser"

test:
	docker-compose exec backend bash -c "python manage.py test"

backend-bash:
	docker-compose exec backend bash