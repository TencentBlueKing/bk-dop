#!/bin/bash

crontab -r -u elastic
supervisorctl stop all
pkill  -f python
mv /data/esenv /data/esenv.`date +%Y%m%d_%H%M%S`
mv /data/esdata /data/esdata.`date +%Y%m%d_%H%M%S`