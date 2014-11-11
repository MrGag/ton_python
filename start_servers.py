# *-* coding:utf-8 *-*
# Запуск всех серверов

import subprocess
from os import chdir, environ
from os.path import dirname, realpath, sep

# Позволяет запускать из консоли
python_path = dirname(realpath(__file__)) + sep + ":" + dirname(realpath(__file__)) + sep + "src" + sep
environ["PYTHONPATH"] = environ.get("PYTHONPATH", "") + python_path

chdir("src/get_sentiment_server")
server_sent = subprocess.Popen(["python", "server_sentiment.py"])
chdir("..")
chdir("..")
    
chdir("src/web_ui")
server_web_ui = subprocess.Popen(["python", "server_web_ui.py"])
chdir("..")
chdir("..")
    
# Test
# chdir("test_documents_server")
# server_test_docs = subprocess.Popen(["python", "test_docs.py"])
# chdir("..")
######
    
f = open("servers_pid.txt", "w")
f.write(str(server_sent.pid) + "\n")
f.write(str(server_web_ui.pid) + "\n")
# Test
# f.write(str(server_test_docs.pid))
######
f.close()

print("Сервисы запущенны")