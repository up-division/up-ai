import subprocess
import json
import os
import requests
import patoolib
import sys
import ctypes
import re
from board_check import scan_boardid

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, os.path.abspath(__file__)+"".join(sys.argv[3:]), None, 1)
    except Exception as e:
        print(f"Error: Unable to restart the program as an administrator。{str(e)}")
        sys.exit(1)
        
def get_filename_from_cd(cd):
    """
    Get file name from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename="(.+)"', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def detect_hardware_by_multiple_pid_vid(targets):
    try:
        result = subprocess.run(['wmic', 'path', 'win32_pnpentity', 'get', 'deviceid'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return "Error: Unable to detect hardware information。"
        
        output = result.stdout.lower()
        detected_hardware = []
        for target in targets:
            for vid_pid in target['vid_pid']:
                if vid_pid['vid'].lower() in output and vid_pid['pid'].lower() in output:
                    detected_hardware.append((target['driver_name'], target['driver_location']))
                    break
        return detected_hardware
    
    except Exception as e:
        return f"Error: {str(e)}"
    
def is_compressed_file(file_path):
    compressed_extensions = ['.zip', '.tar', '.gz', '.bz2', '.7z']
    return any(file_path.endswith(ext) for ext in compressed_extensions)

def download_and_extract(url, extract_to='./drivers'):
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
        if("https://aaeon365-my.sharepoint.com/" in url):
            # Make GET request with allow_redirect
            res = requests.get(url, allow_redirects=True)

            if res.status_code == 200:
                # Get redirect url & cookies for using in next request
                new_url = res.url
                cookies = res.cookies.get_dict()
                for r in res.history:
                    cookies.update(r.cookies.get_dict())
    
                # Do some magic on redirect url
                new_url = new_url.replace("onedrive.aspx","download.aspx").replace("?id=","?SourceUrl=")

                # Make new redirect request
                response = requests.get(new_url, cookies=cookies)
    
                if response.status_code == 200:
                    local_filename = os.path.join(extract_to,get_filename_from_cd(response.headers.get('content-disposition')))
                    with open(local_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    print("File downloaded successfully!")
                else:
                    print("Failed to download the file.")
                    print(response.status_code)
        
        else:
            local_filename = os.path.join(extract_to, url.split('/')[-1])
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        if  local_filename and is_compressed_file(local_filename):              
            patoolib.extract_archive(local_filename, outdir=extract_to)
        return extract_to
    
    except Exception as e:
        return f"Error: {str(e)}"

def find_driver_in_directory(driver_name, directory='./drivers'):
    for root, _, files in os.walk(directory):
        for file in files:
            if driver_name in file and file.endswith(('.inf', '.exe', '.msi')):
                return os.path.join(root, file)
    return None

def install_driver(driver_path):
    try:
        if driver_path.endswith('.inf'):
            result = subprocess.run(['pnputil', '/add-driver', driver_path, '/install'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif driver_path.endswith('.exe'):
            result = subprocess.run([driver_path, '/silent'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        elif driver_path.endswith('.msi'):
            result = subprocess.run(['msiexec', '/i', driver_path, '/quiet'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        else:
            return f"Error: Unsupported driver file type {driver_path}。"
        
        if result.returncode != 0:
            return f"Error: Unable to install the driver {driver_path}。"
        
        return f"Driver installed successfully {driver_path}。"
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    is_up_board=scan_boardid()
    if not is_up_board:
        print("Sorry!is not support device!")
        return
    original_cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if not is_admin():
        run_as_admin()
    else:
        with open('config.json', 'r') as file:
            targets = json.load(file)

        detected_hardware = detect_hardware_by_multiple_pid_vid(targets)
        

        if isinstance(detected_hardware, str):
            print(detected_hardware)
        else:
            for driver_name, driver_location in detected_hardware:
                if driver_location.startswith('http'):
                    extracted_path = download_and_extract(driver_location, extract_to='./drivers')
                    if not extracted_path.startswith('Error'):
                        driver_path = find_driver_in_directory(driver_name, directory=extracted_path)
                        if driver_path:
                            print(install_driver(driver_path))
                        else:
                            print(f"Error: Driver not found {driver_name}。")
                else:
                    if os.path.isdir(driver_location):
                        driver_path = find_driver_in_directory(driver_name, directory=driver_location)
                        if driver_path:
                            print(install_driver(driver_path))
                        else:
                            print(f"Error: Driver not found {driver_name}。")
                    else:
                        print(install_driver(driver_location))

    os.chdir(original_cwd)

if __name__ == "__main__":
    main()