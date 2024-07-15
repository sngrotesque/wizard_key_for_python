import subprocess

professional_edition = [
    "W269N-WFGWX-YVC9B-4J6C9-T83GX", # 推荐使用此密钥
    "236TW-X778T-8MV9F-937GT-QVKBB",
    "87VT2-FY2XW-F7K39-W3T8R-XMFGF",
    "KH2J9-PC326-T44D4-39H6V-TVPBY",
    "TFP9Y-VCY3P-VVH3T-8XXCC-MF4YK",
    "J783Y-JKQWR-677Q8-KCXTF-BHWGC",
    "C4M9W-WPRDG-QBB3F-VM9K8-KDQ9Y",
    "2VCGQ-BRVJ4-2HGJ2-K36X9-J66JG",
    "MGX79-TPQB9-KQ248-KXR2V-DHRTD",
    "FJHWT-KDGHY-K2384-93CT7-323RC"
]

other_edition = [
    # 未知版本的密钥
    "6K2KY-BFH24-PJW6W-9GK29-TMPWP",
    "RHTBY-VWY6D-QJRJ9-JGQ3X-Q2289",
    # 企业版
    "NPPR9-FWDCX-D2C8J-H872K-2YT43",
    # 家庭版
    "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99",
    # 教育版
    "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2",
    # 专业版N
    "MH37W-N47XK-V7XM9-C7227-GCQG9",
    # 企业版N
    "DPH2V-TTNVB-4X9Q3-TJR4H-KHJW4",
    # 教育版N
    "2WH4N-8QGBV-H22JP-CT43Q-MDWWJ",
    # 企业版LSTB
    "WNMTR-4C88C-JK8YV-HQ7T2-76DF9",
    # 企业版LSTB N
    "2F77B-TNFGY-69qqF-B8YKP-D69TJ"
]

def win10_license(key :str, activate_server :str = None):
    def run(cmd :str):
        return subprocess.call(cmd, shell=True)
    # 删除当前产品密钥
    run(f'slmgr /upk')
    # 安装用户选定的产品密钥
    run(f'slmgr /ipk {key}')
    # 更改激活服务器
    if activate_server:
        run(f'slmgr /skms {activate_server}')
    # 开始激活系统
    run(f'slmgr /ato')
