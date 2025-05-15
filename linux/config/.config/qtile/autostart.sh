#!/bin/bash

# Start dbus session if not already running and export env variables
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    eval $(dbus-launch --sh-syntax --exit-with-session)
    export DBUS_SESSION_BUS_ADDRESS
    export DBUS_SESSION_BUS_PID
fi

# Add other startup commands below if needed
# e.g., picom, nm-applet, etc.
