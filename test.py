import subprocess

timeout = 10
result = subprocess.call("cd /root/workspace && timeout 5 python main.py", timeout=timeout, shell=True)
if result == 1:
    raise Exception
