import os
import asyncio
from main import getFiles, downloadFiles, header
from pprint import pprint


OneDriveShareURL = "https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r"
OneDriveSharePwd = "xkx"

aria2Link = "http://localhost:5800/jsonrpc"
aria2Secret = "123456"

isDownload = False
downloadStart = 1
downloadNum = -1


os.environ['PYPPETEER_HOME'] = os.path.split(os.path.realpath(__file__))[0]
# os.environ['PYPPETEER_DOWNLOAD_HOST'] = "http://npm.taobao.org/mirrors"

from pyppeteer import launch

pheader = {}
url = ""


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
    global header
    print("正在启动无头浏览器模拟输入密码")
    asyncio.get_event_loop().run_until_complete(main(iurl, password))
    print("无头浏览器关闭，正在获取文件列表")
    header['cookie'] = pheader["set-cookie"]
    print(getFiles(url, None, 0))


def havePwdDownloadFiles(iurl, password, aria2URL, token, start=1, num=-1):
    global header
    print("正在启动无头浏览器模拟输入密码")
    asyncio.get_event_loop().run_until_complete(main(iurl, password))
    print("无头浏览器关闭，正在获取文件列表")
    header['cookie'] = pheader["set-cookie"]
    downloadFiles(url, None, 0, aria2URL, token, start=start, num=num)


if __name__ == "__main__":
    if isDownload:
        havePwdDownloadFiles(OneDriveShareURL, OneDriveSharePwd, aria2Link,
                             aria2Secret,  start=downloadStart, num=downloadNum)
    else:
        havePwdGetFiles(OneDriveShareURL, OneDriveSharePwd)
