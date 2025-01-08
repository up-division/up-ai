import os
import subprocess
import argparse
ven_ls={'intel':'8086','hailo':'1e60','nvidia':'10de'}
intel_gpuid=['7d55','46d1','a780']
intel_npuid=['7d1d']
hailo_chipid=['2864']
nvidia_chipid=['24fa']
device_book = [
    {"device_type": "intel_gpu", "ven_id": ven_ls['intel'], "sup_chip_ls": intel_gpuid},
    {"device_type": "intel_npu", "ven_id": ven_ls['intel'], "sup_chip_ls": intel_npuid},
    {"device_type": "hailo",     "ven_id": ven_ls['hailo'], "sup_chip_ls": hailo_chipid},
    {"device_type": "nvidia_gpu","ven_id": ven_ls['nvidia'], "sup_chip_ls": nvidia_chipid}
]
version='alpha'

# ========================================
# device_type|ven_id|sup_chip_ls
# -----------------------------------------
# intel_gpu  |8086  |['7D55','46D1','A780']
# intel_npu  |8086  |['7D1D']
# hailo      |8086  |['2864']
# nvidia_gpu |8086  |['24FA']
# =========================================

def arg_parser():
    """Initialize argument parser for the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-dir", "--now_dir", help="now dir", default="./"
    )
    parser.add_argument(
        "-chip", "--scanf_chip", action="store_true",default=False, help="scanf chip"
    )#直接showdevice
    parser.add_argument(
        "-driv", "--install_driver", action="store_true",default=False,help="scanf_driver"
    )
    parser.add_argument(
        "-env", "--create_run", action="store_true",default=False,help="create run"
    )
    parser.add_argument(
        "-at", "--app_type", type=int,default=0,help="what demo type want run?"
    )
    parser.add_argument(
        "-v", "--version", action="store_true",default=False,help="show version"
    )
    return parser

def scanf_chip(book):
    chip_data = subprocess.run(['lspci', '-n'], capture_output=True, text=True)
    lines = chip_data.stdout.splitlines()
    lines = ''.join(lines)
    finded_chip_book=[]
    #intel gpu
    for chip_type_info in book:
        for sup_chipid in chip_type_info['sup_chip_ls']:
            w_instid=chip_type_info['ven_id']+':'+sup_chipid
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
    
def install_driver(book):
    driver_installation_dir=os.path.join(os.getcwd(),'app')
    
    for find_chip_type_info in book:
        if find_chip_type_info['device_type']=='intel_gpu':
            try:
                install_script_path = os.path.join(driver_installation_dir, 'install_igpu.sh')
                os.system(f"bash {install_script_path}")
            except Exception as e:
                print("install error :")
                print(e)
        if find_chip_type_info['device_type']=='intel_npu':
            try:
                install_script_path = os.path.join(driver_installation_dir, 'install_npu.sh')
                os.system(f"bash {install_script_path}")
            except Exception as e:
                print("install error :")
                print(e)
        if find_chip_type_info['device_type']=='hailo':
            try:
                install_script_path = os.path.join(driver_installation_dir, 'install_hailo.sh')
                os.system(f"bash {install_script_path}")
            except Exception as e:
                print("install error :")
                print(e)
        if find_chip_type_info['device_type']=='nvidia_gpu':
            pass
            try:
                install_script_path = os.path.join(driver_installation_dir, 'install_gpu.sh')
                os.system(f"bash {install_script_path}")
            except Exception as e:
                print("install error :")
                print(e)

def build_runspace(book,build_demo_type):
    env_dir=os.path.join(os.getcwd(),'env_list')
    device_dict=scanf_chip(book)
    framework_env={}
    obj_dect_env={'Intel':'ov-obj_det.sh','hailo':'hailo-obj_det.sh','nvidia_gpu':'pytorch-obj_det.sh'}
    cahtbot_env={'Intel':'ov-chatbot.sh'}

    device_map = {
        "Intel": ["Intel", "intel_gpu", "intel_npu"],
        "hailo": ["hailo"],
        "nvidia_gpu": ["nvidia_gpu"]
    }
    inverse_device_map = {}
    for key, values in device_map.items():
        for value in values:
            inverse_device_map[value] = key

    if build_demo_type==0:
        framework_env={'obj_dect':obj_dect_env, 'chatbot':cahtbot_env}
    elif build_demo_type==1:
        #objdet
        framework_env={'obj_dect':obj_dect_env}

    elif build_demo_type==2:
        #chatbot
        framework_env={'chatbot':cahtbot_env}
    for demo_type,demo_env in framework_env.items():
        ov_installed_flag = False
        for device_book in device_dict:
            device_book['device_type']=inverse_device_map.get(device_book['device_type'], "undefined")
            if device_book['device_type']=='Intel' and not ov_installed_flag:
                script_file=os.path.join(env_dir,demo_env[device_book['device_type']])
                os.system(f"bash {script_file}")
                ov_installed_flag = True
            elif device_book['device_type']=='Intel' and ov_installed_flag:
                break
            elif device_book['device_type'] in demo_env:
                script_file=os.path.join(env_dir,demo_env[device_book['device_type']])
                os.system(f"bash {script_file}")
            else:
                continue
    
if __name__ == '__main__':
    args = arg_parser().parse_args()
    if args.version:
        print('=====================================')
        print('Version:'+str(version))
        print('=====================================')
    if args.install_driver:
        install_driver(scanf_chip(device_book))
    if args.scanf_chip:
        installed_driver_book=scanf_chip(device_book)
    if args.create_run:
        build_runspace(device_book,args.app_type)