import os
import signal
from subprocess import Popen


process_list = []
print("Start 5 clients (s)\nClose all cliets (q)\nExit (anything)")

while True:
    choise = input("Your choise: ")
    if choise == "start":
        cmd = [
            "gnome-terminal",
            "--disable-factory",
            "--",
            "python",
            "./client.py",
            "127.0.0.1",
        ]
        for i in range(5):
            process_list.append(
                Popen(cmd if i != 4 else cmd + ["send"], preexec_fn=os.setpgrp)
            )
    elif choise == "close":
        while process_list:
            process = process_list.pop()
            os.killpg(process.pid, signal.SIGINT)
    else:
        break
