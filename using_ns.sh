#!/bin/sh

for DOMAIN in `cat $2`
do
    dig -t NS +short $DOMAIN | grep -q $1 && echo $DOMAIN
done