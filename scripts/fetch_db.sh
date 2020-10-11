#!/bin/sh

TARGET='https://winglers-liste.herokuapp.com'

curl ${TARGET}/api/fetchdb | base64 -d >$PWD/app.db_fetched
