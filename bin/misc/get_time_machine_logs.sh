(base) hrm/modes % printf '\e[3J' && log show --predicate 'subsystem == "com.apple.TimeMachine"' --info --last 6h | grep -F 'eMac' | grep -Fv 'etat' | awk -F']' '{print substr($0,1,19), $NF}' >tmp/time.log

