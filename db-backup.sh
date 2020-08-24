#!/bin/bash
echo "copying current records to db-init."
echo "db-init will be used to init db on next run"
echo ""
echo "backup old db-init to /tmp/bkp-db-init.$$"
#cat db-init > /tmp/bkp-OLD__db-init.$$
cat db-init-records    > /tmp/bkp-db-init-records.$$
cat db-init-deposits   > /tmp/bkp-db-init-deposits.$$
cat db-init-withdraws  > /tmp/bkp-db-init-withdraws.$$

sleep 1s
./show-records.sh   > db-init-records
./show-deposits.sh  > db-init-deposits
./show-withdraws.sh > db-init-withdraws


