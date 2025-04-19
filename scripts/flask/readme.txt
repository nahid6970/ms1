go to advanced firewall
inbound
port
5000
next
next
ok


New-NetFirewallRule -DisplayName "@Allow Port 5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any

New-NetFirewallRule -DisplayName "@Allow Port 5001" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any

New-NetFirewallRule -DisplayName "@Allow Port 5002" -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any