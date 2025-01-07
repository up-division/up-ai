import os
import subprocess
# up_board=['UPN-EDGE-ASLH01','UPX-MTL01','UPV-EDGE-RPL01']
upboard_series=['UP-','UPX','UPS','UPN','UPV']
def scan_boardid():
    find_driver_command='(Get-WmiObject Win32_ComputerSystem Model).Model'
    try:
        result = subprocess.run(["powershell", "-Command", find_driver_command], capture_output=True, text=True)
    except Exception as e:
        print(e)
    if result.stdout.strip()[0:3] in upboard_series:
        return True
    else:
        return False
    # return result.stdout
# scan_boardid()
