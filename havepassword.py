import os
import asyncio
import requests
import re
import json
import urllib

os.environ['PYPPETEER_HOME'] = os.path.split(os.path.realpath(__file__))[0]
os.environ['PYPPETEER_DOWNLOAD_HOST'] = "http://npm.taobao.org/mirrors"

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

from pyppeteer import launch

pheader = {}
url = ""


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


async def main(iurl, password):
    global pheader, url
    browser = await launch()
    page = await browser.newPage()
    await page.goto(iurl, {'waitUntil': 'domcontentloaded'})
    await page.focus("input[id='txtPassword']")
    await page.keyboard.type(password)
    verityElem = await page.querySelector("input[id='btnSubmitPassword']")
    print("密码输入完成，正在跳转")
    await asyncio.gather(
        page.waitForNavigation(),
        verityElem.click(),
    )
    await page.screenshot({'path': 'example.png'})
    p = await page.reload()
    print("正在获取Cookie")
    # print(p.headers, p.url)
    pheader = p.headers
    url = p.url
    await browser.close()


def havePwdGetFiles(iurl, password):
    print("正在启动无头浏览器模拟输入密码")
    asyncio.get_event_loop().run_until_complete(main(iurl, password))
    print("无头浏览器关闭，正在获取文件列表")
    header['cookie'] = pheader["set-cookie"]
    getFiles(url, None, 0)


havePwdGetFiles(
    'https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r', "xkx")
