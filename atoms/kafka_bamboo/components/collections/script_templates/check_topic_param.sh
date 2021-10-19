#!/bin/bash

bootstrap_server="$1"
topic_name="$2"
bootstrap_server_port=$(echo "$1" | awk -F ':' '{print $2}')

if lsof -i:"${bootstrap_server_port}" >/dev/null 2>&1;
then
  /data/kafkaenv/confluent/bin/kafka-configs --bootstrap-server "${bootstrap_server}" --entity-type topics --entity-name "${topic_name}" --describe -all | awk '{print $1}'
  exit 0
else
  exit 1
fi