#!/bin/bash

APP_CODE=${APP_CODE}
ASSET_DIR='static/assets'
IGNORE='*.map,index_dev.html'

pip install coscmd

coscmd config -a ${SID} -s ${SKEY} -b ${BUCKET} -r ${REGION}

coscmd list

echo 'y' | coscmd delete -r ${APP_CODE}/test
coscmd upload -rs ../${ASSET_DIR} ${APP_CODE}/test/${ASSET_DIR} --ignore ${IGNORE}
#coscmd upload -rs --delete ../${ASSET_DIR} ${APP_CODE}/test/${ASSET_DIR} --ignore ${IGNORE}

echo 'y' | coscmd delete -r ${APP_CODE}/prod
coscmd upload -rs ../${ASSET_DIR} ${APP_CODE}/prod/${ASSET_DIR} --ignore ${IGNORE}
#coscmd upload -rs --delete ../${ASSET_DIR} ${APP_CODE}/prod/${ASSET_DIR} --ignore ${IGNORE}

coscmd list ${APP_CODE} -ar --human