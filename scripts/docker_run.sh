#!/bin/sh

docker run -d \
	-p80:5000 \
	--rm \
	--mount 'type=volume,source=wishlist-db,dst=/home/wishlist/db' \
	--name wishlist-app \
	wishlist:latest
