#!make

prepare:
	pip install -r requirements.txt

test:
	cd test_hangmanapi && pytest -v

api-up:
	cd hangmanapi && export FLASK_APP=hangman_api.py && python -m flask run