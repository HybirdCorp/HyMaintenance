# HyMaintenance

If you want to contribute, don't forget to add pre-commit hocks.
```
invoke install-precommit
```

To run lint checks (black, isort and flake8), run this command:
```
invoke lints
```

If needed, to apply black and isort proposed corrections run this command:
```
invoke autolints
```

Here is the contribution workflow :
* assigned you on a ticket
* create a new branch from master with your pseudo at the begin of the branch's name
* code and don't forget to add tests on your modification
* create a pull request with your modification
