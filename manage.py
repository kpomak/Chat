from subprocess import Popen, CREATE_NEW_CONSOLE


process_list = []
print("Start 5 clients (start)\nClose all cliets (close)\nExit (anything)")

while True:
    choise = input("Your choise: ")
    if choise == "start":
        cmd = "python client.py 127.0.0.1"
        for i in range(5):
            process_list.append(
                Popen(
                    cmd if i != 4 else cmd + " send", creationflags=CREATE_NEW_CONSOLE
                )
            )
    elif choise == "close":
        while process_list:
            process = process_list.pop()
            process.kill()
    else:
        break
