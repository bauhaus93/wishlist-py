#/bin/sh

if [ -d "${PWD}/scripts" ]; then
	$PWD/scripts/build.sh &&
		heroku login &&
		heroku container:login &&
		heroku container:push web --app=winglers-liste &&
		heroku container:release web --app=winglers-liste
else
	echo "Directory ${PWD}/scripts not existing, aborting!"
	exit 1
fi
