#! /bin/sh

sudo ln -sf $(pwd)/report-sshd-attempts.py /usr/local/bin
cmd="PYTHONPATH=$HOME/.pyenv/versions/3.8.0/lib/python3.8/site-packages python3 /usr/local/bin/report-sshd-attempts.py > /usr/local/log/report-sshd-attempts.log 2>&1"
cron_cmd="@daily $cmd"
( crontab -l 2>/dev/null | grep -v -F "$cmd" ; echo "$cron_cmd" ) | crontab -

