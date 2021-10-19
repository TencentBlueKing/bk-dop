#!/bin/bash

create_topic(){
   if /data/kafkaenv/confluent/bin/kafka-topics  --bootstrap-server "$1" --create   --topic "$2" --partitions "$6" --replication-factor "$7" --config retention.ms="$3" --config retention.bytes="$4" --config max.message.bytes="$5";
   then
      exit 0
   else
      exit 1
   fi
}

create_topic "$@"
