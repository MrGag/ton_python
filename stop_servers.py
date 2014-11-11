# *-* coding:utf-8 *-*
# Остановка всех серверов

from os import kill, remove

f = open("servers_pid.txt", "r")
for row in f:
    try:
        kill(int(row), 15)
    except KeyboardInterrupt:
        exit()
    except:
        print("Ошибка, PID: {0}".format(row))
f.close()
remove("servers_pid.txt")    
print("Все серверы остановлены")