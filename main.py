import json
import re
import urllib
import urllib.request
from pprint import pprint
from urllib import parse

import requests

header = {
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'dnt': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'service-worker-navigation-preload': 'true',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'iframe',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
}
# "https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh"
# "https://cokemine-my.sharepoint.com/:f:/g/personal/cokemine_cokemine_onmicrosoft_com/EukJbTMXkhJDrPpNVgZM8oUBmywiHfYgL7TSySrAeokVRw?e=FMaVLz"


def getFiles(originalPath):
    req = requests.session()
    req = req.get(originalPath, headers=header)
    # f=open()

    p = re.search(
        'g_listData = {"wpq":"","Templates":{},"ListData":{ "Row" : ([\s\S]*?),"FirstRow"', req.text)
    jsonData = json.loads(p.group(1))
    redURL = req.url
    redsURL = redURL.split("/")
    downloadURL = "/".join(redsURL[:-1])+"/download.aspx?UniqueId="

    # print(downloadURL)
    for i in jsonData:
        print("文件：", i['FileLeafRef'], "\t独特ID：", i["UniqueId"])


def downloadFiles(originalPath, aria2URL, token):
    req = requests.session()
    req = req.get(originalPath, headers=header)
    # f=open()

    p = re.search(
        'g_listData = {"wpq":"","Templates":{},"ListData":{ "Row" : ([\s\S]*?),"FirstRow"', req.text)
    jsonData = json.loads(p.group(1))
    redURL = req.url
    redsURL = redURL.split("/")
    downloadURL = "/".join(redsURL[:-1])+"/download.aspx?UniqueId="

    # print(downloadURL)

    s2 = parse.urlparse(redURL)
    header["referer"] = redURL
    header["cookie"] = req.headers["Set-Cookie"]
    header["authority"] = s2.netloc

    # .replace("-", "%2D")

    # print(dd, [cc])
    headerStr = ""
    for key, value in header.items():
        # print(key+':'+str(value))
        headerStr += key+':'+str(value)+"\n"

    # print(headerStr)
    for i in jsonData:
        cc = downloadURL+(i["UniqueId"][1:-1].lower())
        dd = dict(out=i["FileLeafRef"],  header=headerStr)
        jsonreq = json.dumps({'jsonrpc': '2.0', 'id': 'qwer',
                              'method': 'aria2.addUri',
                              "params": ["token:"+token, [cc], dd]})
        c = requests.post(aria2URL, data=jsonreq)
        pprint(json.loads(c.text))


if __name__ == "__main__":
    getFiles("https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh")
    downloadFiles("https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh",
                  'http://localhost:5800/jsonrpc', "123456")
