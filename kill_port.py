import os

find_port_str = "netstat -aon|findstr %s"
kill_port_str = "taskkill /f /pid %s"

os.popen(find_port_str%(''))