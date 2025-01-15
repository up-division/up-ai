import os
import subprocess
import argparse
import sys
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
from board_check import scan_boardid
ven_ls={'intel':'8086','hailo':'1E60','nvidia':'10DE'}
intel_gpuid=['7D55','46D1','A780']
intel_npuid=['7D1D']
hailo_chipid=['2864']
nvidia_chipid=['24FA']
device_book = [
    {"device_type": "intel_gpu", "ven_id": ven_ls['intel'], "sup_chip_ls": intel_gpuid},
    {"device_type": "intel_npu", "ven_id": ven_ls['intel'], "sup_chip_ls": intel_npuid},
    {"device_type": "hailo",     "ven_id": ven_ls['hailo'], "sup_chip_ls": hailo_chipid},
    {"device_type": "nvidia_gpu","ven_id": ven_ls['nvidia'], "sup_chip_ls": nvidia_chipid}
]
# ========================================
# device_type|ven_id|sup_chip_ls
# -----------------------------------------
# intel_gpu  |8086  |['7D55','46D1','A780']
# intel_npu  |8086  |['7D1D']
# hailo      |8086  |['2864']
# nvidia_gpu |8086  |['24FA']
# =========================================
version='alpha'

# def check_os():
#     now_os=''
#     if os.name == 'nt':
#         print("Operating System: Windows")
#         now_os='windows'
#     elif os.name == 'posix':
#         print("Operating System: Linux/Unix-like")
#         now_os='linux'
#     else:
#         print(f"Unknown Operating System: {os.name}")
#     return now_os
def arg_parser():
    """Initialize argument parser for the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-dir", "--now_dir", help="now dir", default="./"
    )
    # parser.add_argument(
    #     "-chip", "--scan_chip", action="store_true",default=False, help="scanf chip"
    # )#直接showdevice
    parser.add_argument(
        "-driv", "--install_driver", action="store_true",default=False,help="scan_driver"
    )
    parser.add_argument(
        "-env", "--create_run", action="store_true",default=False,help="create run"
    )
    parser.add_argument(
        "-sd", "--scan_driver", action="store_true",default=False,help="scan_driver"
    )
    parser.add_argument(
        "-at", "--app_type", type=int,default=0,help="what demo type want run?"
    )
    parser.add_argument(
        "-v", "--version", action="store_true",default=False,help="show version"
    )
    return parser

def scan_chip(book):
    # now_os=check_os()
    # have_intel_gpu,have_intel_npu,have_hailo,have_nv=False,False,False,False
    # if os.name == 'nt':
    # chip_data = subprocess.run(['pnputil', '/enum-devices'], capture_output=True, text=True)#1809 not support
    scan_chip_command="Get-WmiObject Win32_PnPEntity | Where-Object { $_.DeviceID -like '*PCI*' } | Select-Object DeviceID, Name"
    chip_data = subprocess.run(["powershell", "-Command", scan_chip_command], capture_output=True, text=True)
    # %SYSTEMROOT%\System32\WindowsPowerShell\\v1.0\\powershell.exe#1809
    lines = chip_data.stdout.splitlines()
    lines = ''.join(lines)
    finded_chip_book=[]
    #intel gpu
    # print(type(chip_data))
    for chip_type_info in book:
        for sup_chipid in chip_type_info['sup_chip_ls']:
            w_instid='VEN_'+chip_type_info['ven_id']+'&DEV_'+sup_chipid
            # print(w_instid)
            if w_instid in lines:
                print('Find '+chip_type_info['device_type'])
                new_chip_type_info=dict(chip_type_info)
                new_chip_type_info['sup_chip_ls']=sup_chipid
                finded_chip_book.append(new_chip_type_info)
                break
    #CPU info
    cpu_info={"device_type": "Intel","ven_id": ven_ls['intel'], "sup_chip_ls": 'CPU'}
    finded_chip_book.append(cpu_info)
    return finded_chip_book
class Installer:
    def __init__(self):
        pass
    def is_connet_net(self,test_url):
        test_url=test_url.split('/')[2]#http://'www.google.com'/
        print('Try to connet {}'.format(test_url))
        res=os.system("ping "+test_url+" -n 1")
        if res == 0:
            print('Connet successfully!')
            return True
        else: 
            print('Connet faild!')
            return False
    
    def download_file(self,download_url,storge_dir):
        download_successed=False
        if not download_url:
            print('Not found file download url!')
            return download_successed
        is_connet=self.is_connet_net(download_url)
        if is_connet:
            print("Download file now!")
            download_successed=True
            try:
                result = subprocess.run(['curl','-L','-o',storge_dir,download_url], capture_output=True, text=True, shell=True)
            except Exception as e:
                print(e)
        return download_successed

    def win_unzip(self,zip_dir,output_dir=''):
        file_dir=zip_dir.split('\\')[:-2]
        file_dir='\\'.join(file_dir)
        file_name_with_ext=os.path.basename(zip_dir)
        file_name_without_ext,file_ext=os.path.splitext(file_name_with_ext)
        if output_dir=='':
            output_dir=os.path.join(file_dir,file_name_without_ext)
        self.build_folder(output_dir)
        unzip_successed=True
        zip_ext=['.zip']#['zip','tar']
        if file_ext in zip_ext:
            try:
                result = subprocess.run(['tar','-xf',zip_dir,'-C',output_dir], capture_output=True, text=True, shell=True)
            except Exception as e:
                print(e)
                unzip_successed=False
        else:
            print('{} not support unzip!'.format(file_ext))
            unzip_successed=False
        return unzip_successed
    def build_folder(self,folder_dir):
        if not os.path.exists(folder_dir):
            os.mkdir(folder_dir)

    def check_install_finish_msg(self,exe_output_msg):
        is_install_sucessully=True
        fail_key_word=['error','fail']
        for key_word in fail_key_word:
            if key_word in exe_output_msg:
                is_install_sucessully=False
                break
        return is_install_sucessully
    
    def exec_installer(self,installer_dir,installer_arg):
        install_status=False
        driver_name=installer_dir.split('\\')[-1]
        installer_type=driver_name.split('.')[-1]
        if installer_type=='exe':
            install_driver_command_ls=[installer_dir,installer_arg]
        elif installer_type=='msi':
            install_driver_command_ls=['msiexec','/i',installer_dir,'/qn','/norestart']
        elif installer_type=='inf':
            install_driver_command_ls=['pnputil','/add-driver',installer_dir,'/install']
        else:
            raise Exception("***unsupport installer type!***")
        print('===Installing {}!==='.format(driver_name))
        try:
            result = subprocess.run(install_driver_command_ls, capture_output=True, text=True).stdout.splitlines()#, shell=True
            install_status=self.check_install_finish_msg(result)
        except Exception as e:
            print(e)       
        return install_status
    
    def need_update_driver(self,old_ver,new_ver):
        #input is string
        #if computer driver is old->output 'true'(need update)
        need_update=False
        new_ver_ls = list(map(int, new_ver.strip().split('.')))
        old_ver_ls = list(map(int, old_ver.strip().split('.')))

        for new_word, old_word in zip(new_ver_ls, old_ver_ls):
            if new_word > old_word:
                return need_update

    def install_driver(self,device_config):
        # driver_name=device_config['driver_url'].split('/')[-1]
        installer_dir=device_config['driver_dir']
        installer_url=device_config['driver_url']
        installer_ext=['.exe','.msi','.inf']#need os

        #check file and download
        installer_folder=os.path.join(os.path.dirname(os.path.realpath(__file__)),'driver')
        file_name_with_ext=os.path.basename(installer_dir)
        #if file_dir only file and add driver default folder
        #如果安裝檔於資料夾內，driver_dir = \aaa.exe ,須補資料夾位置
        if installer_dir.split('\\')[0]=='':
            installer_dir=os.path.join(installer_folder,file_name_with_ext)

        file_name_without_ext,installer_type=os.path.splitext(file_name_with_ext)
        
        #確認資料夾有無存在安裝檔(exe,msi,zip,folder(解壓後))
        unziped_dir=os.path.join(installer_folder,file_name_without_ext)
        if (not os.path.exists(unziped_dir)) and (not os.path.isfile(installer_dir)):#check file is exit
            if self.download_file(installer_url,installer_dir):
                print("The file was downloaded successfully!")
            else:
                raise Exception("***Downloaded file error!***")
        
        ###unzip
        #if customer not unzip in driver folder ,and 
        if  not installer_type in installer_ext :
            unziped_dir=installer_dir.split('.')[:-2]
            unziped_dir='.'.join(unziped_dir)
            if self.win_unzip(installer_dir,unziped_dir):
                #解壓後重新設定檔案路徑
                installer_dir=os.path.join(unziped_dir,device_config['install_file'][1:])
                installer_type=device_config['install_file'].split('.')[-1]
            else:
                raise Exception("***Unzip faild!***")
        #install file
        if self.exec_installer(installer_dir,device_config['install_arg']):
            print("The driver install successfully!")
        else:
            raise Exception("***Install Driver error!***")
        
        # if installer_type=='exe':
        #     install_driver_command_ls=[installer_dir,device_config['install_arg']]
        # elif installer_type=='msi':
        #     install_driver_command_ls=['msiexec','/i',installer_dir,'/qn','/norestart']
        # elif installer_type=='inf':
        #     install_driver_command_ls=['pnputil','/add-driver',installer_dir,'/install']
        # else:
        #     raise Exception("***unsupport installer type!***")
        # try:
        #     result = subprocess.run(install_driver_command_ls, capture_output=True, text=True, shell=True)
        #     install_status=True
        #     print('===Install {} successfully!==='.format(driver_name))
        # except Exception as e:
        #     print('***Install {} Error!!!***'.format(driver_name))
        #     print(e)       
        # # return install_status


    
def install_driver(book):
    # drivre_installation_dir=os.path.join(os.getcwd(),'app')
    import configparser
    installer = Installer()
    config = configparser.ConfigParser()    
    drivre_installation_dir=os.path.dirname(os.path.realpath(__file__))#in /app/
    config.read(os.path.join(drivre_installation_dir,'config.ini'),encoding='UTF-8')
    for find_chip_type_info in book:
        if find_chip_type_info['device_type']=='intel_gpu':
            driver_is_installed=installer.install_driver(config['Intel_GPU'])
        if find_chip_type_info['device_type']=='intel_npu':
            npu_driver_dir = config['Intel_NPU']['driver_dir']
            # if npu_driver_dir.split('\\')[0]=='':
            #     driver_name=npu_driver_dir.split('\\')[-1]
            #     npu_driver_dir=os.path.join(drivre_installation_dir,'driver',driver_name)
            # if not os.path.exists(npu_driver_dir):
            #     print("sorry!please go to intell website download NPU driver:")
            #     print("https://www.intel.com/content/www/us/en/download/794734/intel-npu-driver-windows.html")
            # else:
            import platform
            # win_release = platform.release()
            if sys.getwindowsversion().build >= 22000:
                driver_is_installed=installer.install_driver(config['Intel_NPU'])
            else:
                print('Intel NPU need runing in Windows 11!')
        if find_chip_type_info['device_type']=='hailo':
            driver_is_installed=installer.install_driver(config['Hailo'])
        if find_chip_type_info['device_type']=='nvidia_gpu':
            all_install=['Nvidia_GPU','CUDA']
            for now_insatll in all_install:
                driver_is_installed=installer.install_driver(config[now_insatll])



def scan_driver(book):
    # 调用 PowerShell catch output
    driver_book=[]
    print('Scan Driver Now!!!')
    for find_chip_type_info in book:
        # if find_chip_type_info['device_type']=='intel_gpu':
        if find_chip_type_info['sup_chip_ls']=='CPU':
            new_chip_type_info=dict(find_chip_type_info)
            new_chip_type_info.update({'driver': True})
            driver_book.append(new_chip_type_info)         
            continue
        device_id='PCI\VEN_'+find_chip_type_info['ven_id']+'&DEV_'+find_chip_type_info['sup_chip_ls']
        find_driver_command = 'Get-WmiObject Win32_PnPSignedDriver | Where-Object { $_.DeviceID -like "'+device_id+'*" } | Select-Object DriverVersion'
        result = subprocess.run(["powershell", "-Command", find_driver_command], 
                                capture_output=True, text=True).stdout.splitlines()
        if result[3].strip() :
            print('Driver version: '+result[3])
            print('The {device_type} Driver is ready!'.format(**find_chip_type_info))
            new_chip_type_info=dict(find_chip_type_info)
            new_chip_type_info.update({'driver': True})
            driver_book.append(new_chip_type_info)
            # return True
        else:
            print('{device_type} driver not find!'.format(**find_chip_type_info))
            # return False
    # ====================================================
    # device_type|ven_id|sup_chip_ls           |driver
    # ----------------------------------------------------
    # intel_gpu  |8086  |['7D55','46D1','A780']|True/False
    # intel_npu  |8086  |['7D1D']              |True/False
    # hailo      |8086  |['2864']              |True/False
    # nvidia_gpu |8086  |['24FA']              |True/False
    # =====================================================
    return driver_book
    
def build_runspace(driver_installed_book,build_demo_type):
    # print(driver_installed_book)
    env_bat_dir=os.path.join(os.getcwd(),'env_list','py310')
    # driver_installed=scan_driver(book)
    framework_env={}
    # obj_dect_env={'intel_gpu':'ov-obj_det.bat','intel_npu':'ov-obj_det.bat','hailo':'hailo-obj_det.bat','nvidia_gpu':'pytorch_yolov11.bat'}
    obj_dect_env={'Intel':'ov-obj_det.bat','hailo':'hailo-obj_det.bat','nvidia_gpu':'pytorch_yolov11.bat'}#intel_gpu intel_npu use same envirment
    cahtbot_env={'Intel':'ov-chatbot.bat'}
    #list each brand diff device
    device_map = {
        "Intel": ["Intel","intel_gpu", "intel_npu"],
        "hailo": ["hailo"],
        "nvidia_gpu": ["nvidia_gpu"]
    }
    inevrse_device_map={}#inverse map device
    for key, values in device_map.items():
        for value in values:
            inevrse_device_map[value]=key
            # inevrse_device_map.setdefault(value, []).append(key)
    # print(inevrse_device_map)
    if build_demo_type==0:
        framework_env={'obj_dect':obj_dect_env,'cahtbot':cahtbot_env}
    elif build_demo_type==1:
        #objdet
        framework_env={'obj_dect':obj_dect_env}

    elif build_demo_type==2:
        #chatbot
        framework_env={'cahtbot':cahtbot_env}
    
    for demo_type,demo_env in framework_env.items():
        # demo_type,demo_env=sub_framework_env.key,sub_framework_env.value
        ov_installed_device_flag=False
        for driver_book in driver_installed_book:
            # print(driver_book)
            driver_book['device_type']=inevrse_device_map.get(driver_book['device_type'], "undefined")
            # print(driver_book['device_type'])
            if driver_book['device_type'] not in demo_env:
                #if demo not support device,then pass this
                continue
            #check openvino env installed,if installed then break,because openvino have to many infer device
            if driver_book['device_type']=='Intel' and not ov_installed_device_flag:
                ov_installed_device_flag=True
            elif driver_book['device_type']=='Intel' and ov_installed_device_flag:
                break #openvino env installed

            bat_file=os.path.join(env_bat_dir,demo_env[driver_book['device_type']])
            env_name=demo_env[driver_book['device_type']].split('.')[0]
            env_dir=os.path.join(os.getcwd(),'env')#main folder\env
            env_folder=os.path.join(env_dir,env_name)
            reset_runspace=True
            if os.path.isdir(env_folder):
                reset_runspace=False #if env is created then False
                # os.system("cls")
                print("{} already in system,do you want to reinstall?(y/n)".format(env_name))
                while(1):
                    input_value=input()
                    if input_value=='Y' or input_value=='y':
                        print("Reinstall {} NOW!!!!".format(env_name))
                        print("Cleaning old Run Space!")
                        shutil.rmtree(env_folder)
                        reset_runspace=True
                        break
                    elif input_value=='N' or input_value=='n':
                        print("PASS install {}".format(env_name))
                        break
                    else:
                        # os.system("cls")
                        print("Not invild input!!!!!!!!!!!!!!!!!")

            if reset_runspace and driver_book['driver'] and driver_book['device_type'] in demo_env:  
                try:
                    result = subprocess.run(
                        ["call", bat_file],
                        shell=True,
                        check=True,
                        text=True
                    )
                    print('Build {} with {} successfully!'.format(demo_type,driver_book['device_type']))
                except Exception as e:
                    print("Build Run Space error:")
                    print(e)
            #debug to show none install run-space
            # else:
                # print("{} not support {} in toolkit,please check toolkit version!".format(demo_type,driver_book['device_type']))


if __name__ == '__main__':
    args = arg_parser().parse_args()
    # dir=args.now_dir
    # print(dir)
    if args.version:
        print('=====================================')
        print('Version:'+str(version))
        print('=====================================')
    is_up_board=scan_boardid()
    if not is_up_board:
        print("Sorry!is not support device!")
    else:
        print("Welcome use aaeon toolkit!")
        onboard_chip=scan_chip(device_book)

        if args.install_driver:
            install_driver(onboard_chip)
        # install_driver(dir)
        if args.scan_driver:
            installed_driver_book=scan_driver(onboard_chip)
            print('----------------------------------')
            print('          Scan  Result            ')
            print('----------------------------------')
            for driver_book in installed_driver_book:
                if driver_book['driver']:print('[O]',end="")
                else:                   print('[X]',end="")
                print(driver_book['device_type'])
        if args.create_run:
            installed_driver_book=scan_driver(onboard_chip)
            build_runspace(installed_driver_book,args.app_type)
        # scan_driver()
    







    
