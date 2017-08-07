#!/bin/bash
SERVER=http://127.0.0.1:8764/ping
PAUSE=60
FAILED=0
DEBUG=0

while true 
do
if curl -s --head $SERVER | grep "200 OK" > /dev/null 
		then 
			echo "The HTTP server on is up!" > /dev/null 
		else 
			(echo "Subject: The HTTP server on is down
fi
