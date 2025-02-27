import os
import sys
import subprocess
from board_check import scan_boardid

def clear_screen():
    os.system('cls')
    
main_menu=["Install Environment and Inefrence Data",
           "Auto install all",
           ]

# install_menu=[{"name":"Object Detection","cmd": "python "+os.path.dirname(os.path.realpath(__file__))+"\scanf_driver.py -env -at 1"},
#               {"name":"Chatbot","cmd": "python "+os.path.dirname(os.path.realpath(__file__))+"\scanf_driver.py -env -at 2"}
#            ]

install_menu=[{"name":"Object Detection","cmd": ['start',os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'env_list', 'py310', 'ov-obj-all.bat')]},
              {"name":"Chatbot","cmd": ['start',os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'env_list', 'py310', 'ov-chatbot.bat')]}
           ]

def install_one():
    while True:
        clear_screen()
        print("============ Select Environment Installation ============")
        for index, item in enumerate(install_menu, start=1):
            print(f"{index}. {item['name']}")
        print(f"0. exit")
        try:
            choices = [int(choice) for choice in input("Please input number: ").split(',') if choice.isdigit()]    
            if not choices:
                raise ValueError("Invalid input")
        except ValueError as e:
            print("\033[91mError: {}\033[0m".format(e))
            os.system('pause')
            continue    
        
        try:
            for choice in choices:
                if(choice==0):
                    return
                elif(((choice-1)<len(install_menu)) and (choice>0) ):
                    subprocess.run(install_menu[choice-1]['cmd'], shell=True)
                else:
                    print("\033[91mError: {}\033[0m".format("Invalid input"))
            os.system('pause')
        except ValueError:
            print("\033[91mError: {}\033[0m".format("Invalid input"))
            os.system('pause')
            
# def install_one():
#     while True:
#         clear_screen()
#         print("============ Select Environment Installation ============")
#         for index, item in enumerate(install_menu, start=1):
#             print(f"{index}. {item['name']}")
#         print(f"0. exit")
#         try:
#             choices = [int(choice) for choice in input("Please input number: ").split(',') if choice.isdigit()]    
#             if not choices:
#                 raise ValueError("Invalid input")
#         except ValueError as e:
#             print("\033[91mError: {}\033[0m".format(e))
#             os.system('pause')
#             continue    
        
#         try:
#             for choice in choices:
#                 if(choice==0):
#                     return
#                 elif(((choice-1)<len(install_menu)) and (choice>0) ):
#                     subprocess.run(install_menu[choice-1]['cmd'], shell=True)
#                 else:
#                     print("\033[91mError: {}\033[0m".format("Invalid input"))
#             os.system('pause')
#         except ValueError:
#             print("\033[91mError: {}\033[0m".format("Invalid input"))
#             os.system('pause')

def install_all():
    clear_screen()
    #.....install all
    # os.system("python scanf_driver.py -env -at 0")
    for index, item in enumerate(install_menu, start=1):
        subprocess.run(install_menu[index-1]['cmd'], shell=True)


def main():
    
    is_up_board=scan_boardid()
    if not is_up_board:
        print("Sorry!is not support device!")
        return

    install_one()
    
    # while True:
    #     clear_screen()
    #     print("============       Main Menu       ============")
    #     for index, item in enumerate(main_menu, start=1):
    #         print(f"{index}. {item}")
    #     print(f"0. exit")
    #     try:
    #         choice = int(input("Please input number："))
       
    #         match choice:
    #             case 1:
    #                 install_one()
    #                 continue
    #             case 2:
    #                 install_all()
    #             case 0:
    #                 print("\033[91m{}\033[0m".format("Exit.........."))
    #                 break
    #             case _:
    #                 print("\033[91mError: {}\033[0m".format("Invalid input"))
    #         os.system('pause')
    #     except ValueError:
    #         print("\033[91mError: {}\033[0m".format("Invalid input"))
    #         os.system('pause')

       

    
    
if __name__ == "__main__":
    main()