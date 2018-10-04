

all: test

install:
	pip install -r requirements.txt

auto-isort:
	isort --recursive --atomic ./hymaintenance/

auto-pep8:
	sh script_for_autopep8.sh

black:
	black -l120 hymaintenance

run-lint:
	flake8 --show-source hymaintenance
	isort --recursive --atomic --check-only ./hymaintenance/

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

all_included: autopep8 run-lint run-tests-and-coverage

test: run-tests-and-coverage

ci-test: run-lint run-sqlite-only-tests

.PHONY: all install all_included run-lint ci-test run-only-tests run-sqlite-only-tests auto-pep8 auto-isort test run-sqlite-tests-and-coverage run-tests-and-coverage

