import os

find_task_str = "netstat -aon|findstr %s"
kill_task_str = "taskkill /f /pid %s"

print('Plz input the port number!')
port_num = input()
print('input port num:%s' % (port_num))
netsatat_result = os.popen(find_task_str % port_num).readlines()
print(netsatat_result)
if len(netsatat_result) > 0:
    netstat_list = netsatat_result[0].split()
    print(netstat_list)

    process_id = netstat_list[len(netstat_list) - 1]
    print(port_num)

    whatsup = os.popen(kill_task_str % (str(process_id))).readlines()
    print(whatsup)
else:
    print("this port is not using!!!!")

input("finish!")
