#!/bin/bash

# Usage:
#
# 1, Edit schedule tasks 
#    crontab -e
#
# 2, Add lines as following,
#    # m h  dom mon dow   command
#    29  3   * * *   bash /xxx/.../update.sh
#
# 3, Restart cron and view status
#
#    sudo /sbin/service crond reload
#    sudo /sbin/service crond restart
#    sudo /sbin/service crond status
#    sudo cat /var/spool/cron/USERNAME

CONFIG_FILE=""

get_property()
{
    local prop_key=$1
    local prop_value=`cat ${CONFIG_FILE} | grep ${prop_key} | cut -d'=' -f2`

	echo $prop_value
}

NAME='update'
CODE_PATH=$(get_property 'code-path')
OUTPUT_PATH=$(get_property 'output-path')
LOG_FILE="$OUTPUT_PATH/logs/$NAME.log"

function err_exit() {
    local now=`TZ='Asia/Shanghai' date`
    echo "Failed to update at $now." >> $LOG_FILE
    exit 1
}

# Begin
startDate=`TZ='Asia/Shanghai' date`
echo "Updating at $startDate ..." >> $LOG_FILE

# Update
cd $CODE_PATH \
&& source env/bin/activate \
&& python main.py $CONFIG_FILE $NAME 1>> $LOG_FILE 2>> $LOG_FILE || err_exit

# End
endDate=`TZ='Asia/Shanghai' date`
echo "Updated at $endDate" >> $LOG_FILE

