#!/bin/bash

source command.sh

if [ $# -lt 2 ]; then
    echo -e "usages: \n\t$0 content [savefile]\n"
    exit 1
fi

APP="searcher.py"
CONFIG_FILE="/xxx/config.ini"

run $APP $CONFIG_FILE $@

