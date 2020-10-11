#!/bin/sh

if [ -f "${PWD}/Dockerfile" ]; then
	docker build -t wishlist:latest $PWD
else
	echo "Dockerfile not found in ${PWD}, aborting!"
	exit 1
fi
