#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 <argument> <PID>"
  exit 1
fi

argument=$1
PID=$2

mpstat 6 10 > "${argument}_cpu.txt" &
sar -n TCP 6 10 > "${argument}_tcp.txt" &
sar -n DEV 6 10 > "${argument}_dev.txt" &

sudo /usr/share/bcc/tools/cpudist 60 1 -ep ${PID} > "${argument}_cpudist.txt" &
sudo /usr/share/bcc/tools/syscount -d 60 -Lp ${PID} > "${argument}_syscount.txt" &
sudo /usr/share/bcc/tools/cachestat 60 1 > "${argument}_cache.txt" &
sudo /usr/share/bcc/tools/llcstat 60 > "${argument}_llc.txt" &
sudo /usr/share/bcc/tools/tcprtt -d 60 -ep 4025 > "${argument}_rtt.txt" &

echo "Monitoring started"

sleep 60

echo "Monitoring complete."