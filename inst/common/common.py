import os
import sys

def clear_screen():
    if os.name == 'nt': 
        os.system('cls')
    else:
        os.system('clear')
        
def pause():
    if os.name == 'nt': 
        os.system('pause')
    else:
         os.system('read -p "press any key to continue..."')