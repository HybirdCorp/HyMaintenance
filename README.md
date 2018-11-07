# HyMaintenance

## What is HyMaintenance

HyMaintenance is a free/open-source maintenance-contracts management software developed by Hybird (www.hybird.org).

The purpose of HyMaintenance is to facilitate the communication between our company, which offer maintenance contracts and your client about the evolution of your common maintenance contracts.

This web service allows to manage maintenance contract from two perspectives :
* the manager from our client company can see how many maintenance hours are left and how the credits have been consumed during the last six months;
* the operator from our company, who resolved the issues of your client, can manage all contracts of his projects.

It is designed by projects comprised of three different types of maintenance contracts for one company.

## Installation

### Dependencies

(exact versions are indicated in the file `requirements.txt`)
```
- Core
    - Python 3.6+
    - Django 2.0
    - Factory Boy 2.10.0
    - Python crontab 2.2.8
    - Python dateutil 2.7.2
- Dev
    - Black 18.6b2
    - Coverage 4.5.1
    - Django debug toolbar 1.9.1
    - Django extensions 2.0.6
    - Django grappelli 2.11.1
    - Django ordered model 1.4.3
    - Flake8 3.5.0
    - Pycodestyle 2.3.1
    - Ipython 6.2.1
    - Isort 4.3.4
    - Psycopg2 2.7.4
    - Pytz 2018.3
    - Raven 6.6.0
    - Tox 2.9.1
```

### Before HyMaintenance

In the first place, here is the list of softwares you have to install before installating HyMaintenance.
Install python3:
```
sudo apt-get install python3
```
Install git:
```
sudo apt-get install git
``` 

*Optional: you may install virtualenv*
Install virtualenv:
```
sudo apt-get install python3-pip
pip3 install virtualenv
```
Install virtualenvwrapper:
```
sudo apt-get install virtualenvwrapper
```

### HyMaintenance installation
Then, here are instructions you have to follow to install HyMaintenance.
Clone git repository:
```
git clone https://github.com/HybirdCorp/HyMaintenance.git
```
Create a virtual environnement:
```
cd HyMaintenance
mkvirtualenv <nom_venv>
```
Activate your virtual environnement:
```
workon <nom_venv>
```
Install all the python libs needed listed in the file requirements.txt:
```
pip install -r requirements.txt
```
Create a administrator user on your HyMaintenance.
```
cd hymaintenance
python manage.py create_admin
```
If you didn't have PostgreSQL installed, add the option `--settings`:
```
python manage.py create_admin --settings=hymaintenance.sqlite_tests_settings
```

## Run HyMaintenance
To run HyMaintenance:
```
python manage.py runserver
```
If you didn't have PostgreSQL installed, like in the installation, add the option `--settings`:
```
python manage.py runserver --settings=hymaintenance.sqlite_tests_settings
```
## Developers
If you want to contribute, don't forget to add pre-commit hock.
```
cp precommit_script.py .git/hooks/pre-commit
```

Here is the contribution workflow :
* assigned you on a ticket
* create a new branch from master with your pseudo at the begin of the branch's name
* code and don't forget to add tests on your modification
* create a pull request with your modification
