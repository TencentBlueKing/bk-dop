#!/bin/bash

ENV_FILE=$1

for va in `cat $ENV_FILE | sed -e '/^$/d'`;
do
  if [[ ! "$va" =~ ^# ]]; then
      echo "export $va;"
      export $va;
  fi
done
