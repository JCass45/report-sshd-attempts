#! /bin/sh

cmd="python /usr/local/bin/report-sshd-attempts.py > /usr/local/log/report-sshd-attempts.log 2>&1"
cron_cmd="@daily $cmd"
( crontab -l 2>/dev/null | grep -v -F "$cmd" ; echo "$cron_cmd" ) | crontab -

