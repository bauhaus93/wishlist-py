#!/bin/sh

git pull --ff-only
$PWD/venv/bin/pip install -q -r requirements.txt
$PWD/scripts/run.sh
