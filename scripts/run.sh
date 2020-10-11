#!/bin/sh

if [ -z ${PORT} ]; then
	PORT='5000'
fi

if [ -d "${PWD}/venv" ]; then
	$PWD/venv/bin/flask db upgrade
	$PWD/venv/bin/gunicorn -b :${PORT} --access-logfile - --error-logfile - wishlist:app
else
	echo "Directory ${PWD}/venv not existing, aborting!"
	exit 1
fi
