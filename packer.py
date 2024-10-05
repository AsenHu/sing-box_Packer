import requests
import shutil
import os
import tarfile

# GitHub API URLs
BOX_RELEASES_URL = "https://api.github.com/repos/SagerNet/sing-box/releases/latest"
BOX_PACKER_URL = "https://api.github.com/repos/AsenHu/sing-box_Packer/releases/latest"

def get_latest_tag(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['tag_name']

def get_packer_latest_tag(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['tag_name']
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            return "v0.0.0"
        else:
            raise err

def download_file(url, file_name):
    response = requests.get(url)
    response.raise_for_status()
    with open(file_name, 'wb') as file:
        file.write(response.content)

def main():
    # 获取最新标签
    box_latest = get_latest_tag(BOX_RELEASES_URL)
    box_packer_latest = get_packer_latest_tag(BOX_PACKER_URL)

    print(f"Latest sing-box version: {box_latest}")
    print(f"Latest sing-box_Packer version: {box_packer_latest}")

    # 检查更新
    if box_latest == box_packer_latest:
        print("No updates available.")
        return

    # 下载文件
    print("Downloading hath-rust binaries...")
    download_file(f"https://github.com/SagerNet/sing-box/releases/download/{box_latest}/sing-box-{box_latest.lstrip('v')}-linux-amd64.tar.gz", "sing.tar.gz")
    download_file(f"https://github.com/SagerNet/sing-box/releases/download/{box_latest}/sing-box-{box_latest.lstrip('v')}-linux-amd64v3.tar.gz", "singv3.tar.gz")

    # 准备工作
    os.makedirs('deb/usr/bin', exist_ok=True)
    with open('deb/DEBIAN/control', 'a') as file:
        file.write(f'Version: {box_latest.lstrip('v')}\n')

    # 打包成 deb
    # amd64
    print("Packaging into .deb files...")
    with tarfile.open('sing.tar.gz', 'r:gz') as tar:
        sing = tar.extractfile(f"sing-box-{box_latest.lstrip('v')}-linux-amd64/sing-box")
        with open('deb/usr/bin/sing-box', 'wb') as file:
            file.write(sing.read())
    os.system('dpkg-deb -Zxz -Sextreme -z9 -vD -b ./deb sing-box.deb')
    # amd64v3
    with tarfile.open('singv3.tar.gz', 'r:gz') as tar:
        sing = tar.extractfile(f"sing-box-{box_latest.lstrip('v')}-linux-amd64v3/sing-box")
        with open('deb/usr/bin/sing-box', 'wb') as file:
            file.write(sing.read())
    os.system('dpkg-deb -Zxz -Sextreme -z9 -vD -b ./deb sing-boxv3.deb')

    # tag name for 工作流
    with open('tag_name.txt', 'w') as file:
        file.write(box_latest)

if __name__ == "__main__":
    main()