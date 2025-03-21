import os
import subprocess
from common import clear_screen,pause



    
# apps = [{"app":"Object Detection - video","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run', 'obj.bat'),'1']},
#         {"app":"Object Detection - camera","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)),'run', 'obj.bat'),'2']},
#         {"app":"Chatbot","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run', 'chatbot.bat')]}
#         ]  

apps_win = [{"app":"Object Detection - video","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', '..', 'demos','obj-detect', 'run.bat'),'1']},
        {"app":"Object Detection - camera","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', '..', 'demos','obj-detect', 'run.bat'),'2']},
        {"app":"Chatbot","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)),'..', '..', 'demos','chatbot', 'run.bat')]}
        ]  

apps_linux = [{"app":"Object Detection - video","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run', 'obj.bat'),'1']},
        {"app":"Object Detection - camera","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)),'run', 'obj.bat'),'2']},
        {"app":"Chatbot","cmd":[os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run', 'chatbot.bat')]}
        ]  

def select_app(choices):


    try:
        for choice in choices:
            if(((choice-1)<len(apps)) and (choice>0) ):
                subprocess.run(apps[choice-1]['cmd'], shell=True)
            else:
                print("\033[91mError: {}\033[0m".format("Invalid input"))
            pause()
    except ValueError:
        print("\033[91mError: {}\033[0m".format("Invalid input"))
        pause()
            

def display_menu():
    clear_screen()
    print("-------------Main Menu-------------")
    for i, app in enumerate(apps, start=1):
            print(f"{i}.{app['app']}")
    print("0.exit")

def main():
    
    while True: 
        display_menu()
        try:
            choices = [int(choice) for choice in input("Please input number: ").split(',') if choice.isdigit()]    
            if not choices:
                raise ValueError("Invalid input")
            elif(0 in choices):
                print("\033[91m{}\033[0m".format("Exit.........."))
                return
        except ValueError as e:
            print("\033[91mError: {}\033[0m".format(e))
            pause()
            continue

        select_app(choices)

if __name__ == "__main__":
    global apps
    if os.name == 'nt': 
        apps=apps_win
    else:
        apps=apps_linux
        


    main()