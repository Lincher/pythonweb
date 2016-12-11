import os

find_port_str = "netstat -aon|findstr %s"
kill_port_str = "taskkill /f /pid %s"

result = os.popen(find_port_str % ('9000')).readlines()
print(result)
result0 = result[0].split()
print(result0)

port_num = result0[len(result0)-1]
print(port_num)

result1 = os.popen(kill_port_str%(str(port_num))).readlines()
print(result1)