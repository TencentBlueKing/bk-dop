#!/bin/bash
# python deploy.py bk_itsm -a 458 -u XX -p XX -d https://paas.bking.com -e test -m gzip -f ./demo.tar.gz
python3 ./deploy.py $APP_CODE -a $APP_ID -u $PAAS_USER -p $PAAS_PASSWD -d $PAAS_DOMAIN -e test -m gzip -f $APP_FILE
