import os

find_port_str = "netstat -aon|findstr %s"
kill_port_str = "taskkill /f /pid %s"

result = os.popen(find_port_str%('9000')).readlines()
print(result)