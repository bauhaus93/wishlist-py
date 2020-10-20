#!/bin/sh

sudo pkill gunicorn
nohup ./scripts/boot.sh &
tail -f nohup.out
