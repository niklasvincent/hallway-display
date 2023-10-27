#!/bin/bash

set -o allexport
source .env-production
set +o allexport

ERSTAGATAN_SITE_ID="1304"
ERSTA_SJUKHUS_SITE_ID="1305"
ASAGATAN_SITE_ID="1308"

curl -vv -X GET "https://api.sl.se/api2/realtimedeparturesV4.json?key=${SL_API_KEY}&siteid=${ASAGATAN_SITE_ID}&timewindow=30" | jq . 

#SL_API_KEY="1dfa0850914a41ffa26c71892af96e7d"
#curl -vv -X GET "https://api.sl.se/api2/typeahead.json?key=${SL_API_KEY}&searchstring=Åsögatan&stationsonly=true&maxresults=10" | jq .
