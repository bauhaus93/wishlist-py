#!/bin/sh

git pull --ff-only
$PWD/venv/bin/pip install -r requirements
$PWD/scripts/run.sh
