

all: test

install:
	pip install -r requirements.txt

auto-isort:
	isort --recursive --atomic ./hymaintenance/

black:
	black -l120 hymaintenance

black-check:
	black --check -l120 hymaintenance

flake8:
	flake8 --show-source hymaintenance

isort:
	isort --recursive --atomic --check-only ./hymaintenance/

lint: flake8 isort black-check

run-tests-and-coverage:
	coverage run --branch --source=hymaintenance hymaintenance/manage.py test hymaintenance --settings hymaintenance.tests_settings
	coverage report -m --omit=hymaintenance/manage.py,**/migrations/*,**/admin.py,hymaintenance/hymaintenance/* --skip-covered

run-sqlite-tests-and-coverage:
	coverage run --branch --source=hymaintenance hymaintenance/manage.py test hymaintenance --settings hymaintenance.sqlite_tests_settings
	coverage report -m --omit=hymaintenance/manage.py,**/migrations/*,**/admin.py,hymaintenance/hymaintenance/* --skip-covered

run-sqlite-only-tests:
	python hymaintenance/manage.py test hymaintenance --parallel=4 --settings=hymaintenance.sqlite_tests_settings --noinput

run-only-tests:
	python hymaintenance/manage.py test hymaintenance --parallel=4 --settings=hymaintenance.tests_settings --noinput

all_included: black lint run-tests-and-coverage

test: run-tests-and-coverage

serve:
	python hymaintenance/manage.py runserver --settings=hymaintenance.dev_settings

migrate:
	python hymaintenance/manage.py migrate --settings=hymaintenance.tests_settings

.PHONY: all install all_included lint run-only-tests run-sqlite-only-tests auto-isort test run-sqlite-tests-and-coverage run-tests-and-coverage serve migrate

