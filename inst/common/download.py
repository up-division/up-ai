import argparse
import requests
import re
import os
import patoolib
from board_check import scan_boardid

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

def is_compressed_file(file_path):
    compressed_extensions = ['.zip', '.tar', '.gz', '.bz2', '.7z']
    return any(file_path.endswith(ext) for ext in compressed_extensions)

def download_and_extract(url, output_dir):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
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
                    local_filename = os.path.join(output_dir,get_filename_from_cd(response.headers.get('content-disposition')))
                    with open(local_filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            f.write(chunk)
                    print("File downloaded successfully!")
                else:
                    print("Failed to download the file.")
                    print(response.status_code)
        
        else:
            local_filename = os.path.join(output_dir, url.split('/')[-1])
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                 
        if local_filename and is_compressed_file(local_filename):              
            patoolib.extract_archive(local_filename, outdir=output_dir)
            if os.path.exists(local_filename):
                os.remove(local_filename)
                print(f"{local_filename} is clean")
            else:
                print(f"{local_filename} is not exist")
    
    except Exception as e:
        print(f"Error: {str(e)}")



def main():
    is_up_board=scan_boardid()
    if not is_up_board:
        print("Sorry!is not support device!")
        return

    parser = argparse.ArgumentParser(description="Download and extract files from a URL.")
    parser.add_argument('-url', metavar='URL link', required=True, help="The URL of the file to download.")
    parser.add_argument('-o', metavar='Output dir', required=True, help="The output directory where files will be extracted.")
    args = parser.parse_args()
    
    download_and_extract(args.url, args.o)

        
if __name__ == "__main__":
    main()
