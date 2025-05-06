#!/bin/bash

while true; do
    xsetroot -name "$(date)"
    sleep 1s
done &

dte() {
    dte="$(date +"%A, %B %d - %I:%M")"
    echo -e " $dte"
}