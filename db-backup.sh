#!/bin/bash
echo "Exporting current records to db-init files."
echo "Make sure to delete records before next run (by running: ./delete-all-records.sh ),"
echo "also make sure to set environment var DB_INIT=TRUE"
echo "before execution to allow db recreate from init files (pokerbot app will exit with 0)"
echo "then unset the environment var for normal execution with the created db."
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


