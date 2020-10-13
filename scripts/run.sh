#!/bin/sh

if [ -z ${PORT} ]; then
	PORT='5000'
fi

if [ ! -d "${PWD}/venv" ]; then
	python3 -mvenv ${PWD}/venv
	$PWD/venv/bin/pip install --upgrade pip
	$PWD/venv/bin/pip install -r requirements.txt gunicorn
fi
source "${PWD}/venv/bin/activate" &&
	flask db upgrade &&
	gunicorn -b :${PORT} --access-logfile gunicorn_access.log --error-logfile gunicorn_error.log wishlist:app
