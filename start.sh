#!/bin/sh
touch /var/log/cron.log
cron
tail -f /var/log/cron.log