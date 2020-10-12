#!/bin/sh

$PWD/scripts/docker_stop.sh
$PWD/scripts/build.sh
$PWD/scripts/docker_run.sh
