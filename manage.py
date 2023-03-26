import os
import signal
from subprocess import Popen


process_list = []
print(f"Start some count of clients (number of clients)\nClose all cliets (q)\nExit (anything)")

while True:
    choise = input("Your choise: ")
    if choise.isdigit():
        cmd = [
            "gnome-terminal",
            "--disable-factory",
            "--",
            "python",
            "./client.py",
            "127.0.0.1",
        ]
        for i in range(int(choise)):
            process_list.append(
                Popen(
                    cmd,
                    preexec_fn=os.setpgrp,
                )
            )
    elif choise == "q":
        while process_list:
            process = process_list.pop()
            os.killpg(process.pid, signal.SIGINT)
    else:
        break
