import subprocess
import sys

# List of board IDs to check
# up_board = ['UPN-EDGE-ASLH01', 'UPX-MTL01', 'UPV-EDGE-RPL01']
up_board = ['UP-', 'UPX', 'UPN', 'UPS', 'UPV']

# Run the dmidecode command and capture its output
try:
    output = subprocess.check_output(['sudo', 'dmidecode', '-t', 'baseboard'], stderr=subprocess.STDOUT, text=True)
    
    # Check if any of the items are found in the dmidecode output
    for item in up_board:
        if item in output:
            sys.exit(0)

except subprocess.CalledProcessError as e:
    print(f"Error running dmidecode: {e.output}")
    sys.exit(1)

sys.exit(1)

# If no board ID is found, display the error message
# if not found:
#     print("Sorry ! This board is not support !")
#     exit(0)