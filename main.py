import json
import re
import urllib
import urllib.request
from pprint import pprint
from urllib import parse

import requests
import os

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


def getFiles(originalPath, req, layers):
    if req == None:
        req = requests.session()
    reqf = req.get(originalPath, headers=header)
    if ',"FirstRow"' not in reqf.text:
        print("\t"*layers, "这个文件夹没有文件")
        return

    f = open("a.html", "w+", encoding="utf-8")
    f.write(reqf.text)
    f.close()

    p = re.search(
        'g_listData = {"wpq":"","Templates":{},"ListData":{ "Row" : ([\s\S]*?),"FirstRow"', reqf.text)
    jsonData = json.loads(p.group(1))
    # print(p.group(1))
    redURL = reqf.url
    new_url = urllib.parse.urlparse(redURL)
    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(redURL).query))
    redsURL = redURL.split("/")
    downloadURL = "/".join(redsURL[:-1])+"/download.aspx?UniqueId="

    # print(query)

    for i in jsonData:
        if i['FSObjType'] == "1":
            print("\t"*layers, "文件夹：",
                  i['FileLeafRef'], "\t独特ID：", i["UniqueId"])
            query['id'] = os.path.join(
                query['id'],  i['FileLeafRef']).replace("\\", "/")
            originalPath = "/".join(redsURL[:-1]) + \
                "/onedrive.aspx?" + urllib.parse.urlencode(query)
            # print(originalPath)
            getFiles(originalPath, req, layers+1)
        else:
            print("\t"*layers, "文件：",
                  i['FileLeafRef'], "\t独特ID：", i["UniqueId"])


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


def getFilesHavePwd(originalPath, password):
    req = requests.session()
    req.cookies.update(header)
    r = req.get(originalPath)
    p = re.search(
        'SideBySideToken" value="(.*?)" />', r.text)
    SideBySideToken = p.group(1)
    p = re.search(
        'id="__VIEWSTATE" value="(.*?)" />', r.text)
    __VIEWSTATE = p.group(1)
    p = re.search(
        'id="__VIEWSTATEGENERATOR" value="(.*?)" />', r.text)
    __VIEWSTATEGENERATOR = p.group(1)
    p = re.search(
        '__EVENTVALIDATION" value="(.*?)" />', r.text)
    __EVENTVALIDATION = p.group(1)
    s2 = parse.urlparse(originalPath)
    redURL = originalPath
    redsURL = redURL.split("/")
    shareQuery = s2.path.split("/")[-1]
    redsURL[-1] = "guestaccess.aspx?"+s2.query+"&share="+shareQuery
    pwdURL = "/".join(redsURL)
    print(pwdURL, r.headers)
    hewHeader = {
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        "connection": "keep-alive",
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        "host": s2.netloc,
        "origin": s2.scheme+"://"+s2.netloc,
        "Referer": originalPath,
        'sec-ch-ua-mobile': '?0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',

    }

    req.cookies.update(header)
    r = req.post(pwdURL, data={
        "__EVENTTARGET": "btnSubmitPassword",
        "__EVENTARGUMENT": None,
        "SideBySideToken": SideBySideToken,
        "__VIEWSTATE": __VIEWSTATE,
        "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
        "__VIEWSTATEENCRYPTED": None,
        "__EVENTVALIDATION": __EVENTVALIDATION,
        "txtPassword": password
    }, headers=hewHeader, allow_redirects=False)
    print(r.headers, r.text)
    new_url = r.headers["Location"]

    r = req.get(new_url,
                headers=r.headers, allow_redirects=False)
    print(r.headers, r.text)


if __name__ == "__main__":
    getFiles("https://gw6-my.sharepoint.com/:f:/g/personal/admin_gwliang_com/EvyrJ1GVBJBCjI42SuqG4yIBFxT-B5tUsyDsTKiZQX97uw?e=jtqYl0", None, 0)
    # downloadFiles("https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh",   'http://localhost:5800/jsonrpc', "123456")
    # getFilesHavePwd(
    #   "https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r&guestaccesstoken=xyz", "xkx")
