#!/bin/bash

dte() {
    dte="$(date +"%A, %B %d - %I:%M")"
    echo -e " $dte"
}

while true; do
    xsetroot -name "$(dte)"
    sleep 1s
done &