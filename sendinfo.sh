#!/bin/bash

. /jd/config/config.sh
title=$(echo $1|sed 's/-/_/g')
#msg=$(echo $2|sed ":a;N;s#\n#<br/>#g;ta")
msg=$(echo -e $2)

#echo $title
#echo $msg

node /jd/scripts/sendinfo.js "$title" "$msg"
