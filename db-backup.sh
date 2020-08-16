#!/bin/bash
echo "copying current records to db-init."
echo "db-init will be used to init db on next run"
echo ""
echo "backup old db-init to /tmp/bkp-db-init.$$"
cat db-init > /tmp/bkp-db-init.$$
sleep 1s
./show-records.sh > db-init
