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

(exact versions are indicated in the file `hymaintenance/requirements/requirements.in`)


### Before HyMaintenance

In the first place, here is the list of softwares you have to install before installing HyMaintenance.
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
Install all python libs needed listed in the file requirements.txt:
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
All instructions are in CONTRIBUTING.txt file.
