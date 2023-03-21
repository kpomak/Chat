import os
import signal
from subprocess import Popen

CLIENTS_COUNT = 3


process_list = []
print(f"Start {CLIENTS_COUNT} clients (s)\nClose all cliets (q)\nExit (anything)")

while True:
    choise = input("Your choise: ")
    if choise == "s":
        cmd = [
            "gnome-terminal",
            "--disable-factory",
            "--",
            "python",
            "./client.py",
            "127.0.0.1",
        ]
        for i in range(CLIENTS_COUNT):
            process_list.append(
                Popen(
                    cmd if i != CLIENTS_COUNT - 1 else cmd + ["send"],
                    preexec_fn=os.setpgrp,
                )
            )
    elif choise == "q":
        while process_list:
            process = process_list.pop()
            os.killpg(process.pid, signal.SIGINT)
    else:
        break
