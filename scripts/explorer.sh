#!/bin/bash

DIR=$(dirname "$0")
source "$DIR/command.sh"

APP=$(basename "$0")
APP=${APP//\.sh/.py}

run $APP $@

