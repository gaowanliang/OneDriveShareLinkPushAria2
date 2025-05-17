import json
import re
import urllib
import urllib.request
import argparse

from pprint import pprint
from urllib import parse

import requests
import os
import copy
import sys
import io

from requests.models import codes
from requests.adapters import HTTPAdapter, Retry

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def parse_arguments():
    parser = argparse.ArgumentParser(description='OneDrive Share Link Push to Aria2')
    parser.add_argument('onedrive_url', help='OneDrive share URL')
    parser.add_argument('--aria2-link', default="http://127.0.0.1:6800/jsonrpc",
                      help='Aria2 JSON-RPC URL (default: http://127.0.0.1:6800/jsonrpc)')
    parser.add_argument('--aria2-secret', default="",
                      help='Aria2 RPC secret (default: "")')
    parser.add_argument('--download', action='store_true',
                      help='Enable download mode (default: False)')
    parser.add_argument('--download-num', default="0",
                      help='Download file numbers, e.g., "1,2-4,5" (default: "0")')
    return parser.parse_args()

fileCount = 0

header = {
    "sec-ch-ua-mobile": "?0",
    "upgrade-insecure-requests": "1",
    "dnt": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "service-worker-navigation-preload": "true",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "navigate",
    "sec-fetch-dest": "iframe",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
}
# "https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh"
# "https://cokemine-my.sharepoint.com/:f:/g/personal/cokemine_cokemine_onmicrosoft_com/EukJbTMXkhJDrPpNVgZM8oUBmywiHfYgL7TSySrAeokVRw?e=FMaVLz"


def newSession():
    s = requests.session()
    retries = Retry(total=5, backoff_factor=0.1)
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def getFiles(originalPath, req, layers, _id=0):
    global fileCount
    # new_url = urllib.parse.urlparse(originalPath)
    # header["host"] = new_url.netloc
    # print(header)
    isSharepoint = False
    if "-my" not in originalPath:
        isSharepoint = True
    if req is None:
        req = newSession()
    reqf = req.get(originalPath, headers=header)
    # f = open("a.html", "w+", encoding="utf-8")
    # f.write(reqf.text)
    # f.close()
    # if ',"FirstRow"' not in reqf.text:
    #     print("\t"*layers, "这个文件夹没有文件")
    #     return 0

    filesData = []

    # print(p.group(1))
    redirectURL = reqf.url
    # print(redirectURL)

    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(redirectURL).query))
    redirectSplitURL = redirectURL.split("/")

    relativeFolder = ""
    rootFolder = query["id"]
    for i in rootFolder.split("/"):
        if isSharepoint:
            if i != "Shared Documents":
                relativeFolder += i + "/"
            else:
                relativeFolder += i
                break
        else:
            if i != "Documents":
                relativeFolder += i + "/"
            else:
                relativeFolder += i
                break
    relativeUrl = (
        parse.quote(relativeFolder)
        .replace("/", "%2F")
        .replace("_", "%5F")
        .replace("-", "%2D")
    )
    rootFolderUrl = (
        parse.quote(rootFolder)
        .replace("/", "%2F")
        .replace("_", "%5F")
        .replace("-", "%2D")
    )

    graphqlVar = (
        '{"query":"query (\n        $listServerRelativeUrl: String!,$renderListDataAsStreamParameters: RenderListDataAsStreamParameters!,$renderListDataAsStreamQueryString: String!\n        )\n      {\n      \n      legacy {\n      \n      renderListDataAsStream(\n      listServerRelativeUrl: $listServerRelativeUrl,\n      parameters: $renderListDataAsStreamParameters,\n      queryString: $renderListDataAsStreamQueryString\n      )\n    }\n      \n      \n  perf {\n    executionTime\n    overheadTime\n    parsingTime\n    queryCount\n    validationTime\n    resolvers {\n      name\n      queryCount\n      resolveTime\n      waitTime\n    }\n  }\n    }","variables":{"listServerRelativeUrl":"%s","renderListDataAsStreamParameters":{"renderOptions":5707527,"allowMultipleValueFilterForTaxonomyFields":true,"addRequiredFields":true,"folderServerRelativeUrl":"%s"},"renderListDataAsStreamQueryString":"@a1=\'%s\'&RootFolder=%s&TryNewExperienceSingle=TRUE"}}'
        % (relativeFolder, rootFolder, relativeUrl, rootFolderUrl)
    )

    # print(graphqlVar, reqf.headers)
    s2 = urllib.parse.urlparse(redirectURL)
    tempHeader = copy.deepcopy(header)
    tempHeader["referer"] = redirectURL
    tempHeader["authority"] = s2.netloc
    tempHeader["content-type"] = "application/json;odata=verbose"
    # print(redirectSplitURL)

    graphqlReq = req.post(
        "/".join(redirectSplitURL[:-3]) + "/_api/v2.1/graphql",
        data=graphqlVar.encode("utf-8"),
        headers=tempHeader,
        cookies=reqf.cookies,
    )
    graphqlReq = json.loads(graphqlReq.text)
    # print(graphqlReq)
    if "NextHref" in graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]:
        nextHref = graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"][
            "NextHref"
        ] + "&@a1=%s&TryNewExperienceSingle=TRUE" % ("%27" + relativeUrl + "%27")
        filesData.extend(
            graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"]
        )
        # print(filesData)

        listViewXml = graphqlReq["data"]["legacy"]["renderListDataAsStream"][
            "ViewMetadata"
        ]["ListViewXml"]
        renderListDataAsStreamVar = '{"parameters":{"__metadata":{"type":"SP.RenderListDataParameters"},"RenderOptions":1216519,"ViewXml":"%s","AllowMultipleValueFilterForTaxonomyFields":true,"AddRequiredFields":true}}' % (
            listViewXml
        ).replace(
            '"', '\\"'
        )
        # print(renderListDataAsStreamVar, nextHref,1)

        # print(listViewXml)

        graphqlReq = req.post(
            "/".join(redirectSplitURL[:-3])
            + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream"
            + nextHref,
            data=renderListDataAsStreamVar.encode("utf-8"),
            headers=tempHeader,
        )
        graphqlReq = json.loads(graphqlReq.text)
        # print(graphqlReq)

        while "NextHref" in graphqlReq["ListData"]:
            nextHref = graphqlReq["ListData"][
                "NextHref"
            ] + "&@a1=%s&TryNewExperienceSingle=TRUE" % ("%27" + relativeUrl + "%27")
            filesData.extend(graphqlReq["ListData"]["Row"])
            graphqlReq = req.post(
                "/".join(redirectSplitURL[:-3])
                + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream"
                + nextHref,
                data=renderListDataAsStreamVar.encode("utf-8"),
                headers=tempHeader,
            )
            # print(graphqlReq.text)
            graphqlReq = json.loads(graphqlReq.text)
            # print(graphqlReq)
        filesData.extend(graphqlReq["ListData"]["Row"])
    else:
        filesData.extend(
            graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"]
        )
    # fileCount = 0
    # 不重置文件计数
    for i in filesData:
        if i["FSObjType"] == "1":
            print(
                "\t" * layers,
                "Folder(文件夹): ",
                i["FileLeafRef"],
                "\tUnique ID: ",
                i["UniqueId"],
            )
            _query = query.copy()
            _query["id"] = os.path.join(_query["id"], i["FileLeafRef"]).replace(
                "\\", "/"
            )
            if not isSharepoint:
                originalPath = (
                    "/".join(redirectSplitURL[:-1])
                    + "/onedrive.aspx?"
                    + urllib.parse.urlencode(_query)
                )
            else:
                originalPath = (
                    "/".join(redirectSplitURL[:-1])
                    + "/AllItems.aspx?"
                    + urllib.parse.urlencode(_query)
                )
            getFiles(originalPath, req, layers + 1, _id=fileCount)
            # fileCount += getFiles(originalPath, req, layers+1, _id=fileCount)
        else:
            fileCount += 1
            print(
                "\t" * layers,
                "Files(文件)[%d]: %s\tUnique ID: %s"
                % (fileCount, i["FileLeafRef"], i["UniqueId"]),
            )
    return fileCount


def downloadFiles(
    originalPath, req, layers, aria2URL, token, num=[0], _id=0, originalDir=""
):
    global fileCount
    if req is None:
        req = newSession()
    # print(header)
    if originalDir == "":
        originalDir = getAria2ConfigDir(aria2URL, token)
    reqf = req.get(originalPath, headers=header)
    isSharepoint = False
    if "-my" not in originalPath:
        isSharepoint = True

    # f=open()
    # if ',"FirstRow"' not in reqf.text:
    #     print("\t"*layers, "这个文件夹没有文件")
    #     return 0

    filesData = []
    redirectURL = reqf.url
    redirectSplitURL = redirectURL.split("/")
    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(redirectURL).query))
    downloadURL = "/".join(redirectSplitURL[:-1]) + "/download.aspx?UniqueId="
    if isSharepoint:
        pat = re.search('templateUrl":"(.*?)"', reqf.text)

        downloadURL = pat.group(1)
        downloadURL = urllib.parse.urlparse(downloadURL)
        downloadURL = "{}://{}{}".format(
            downloadURL.scheme, downloadURL.netloc, downloadURL.path
        ).split("/")
        downloadURL = "/".join(downloadURL[:-1]) + "/download.aspx?UniqueId="
        # print(downloadURL)

    # print(reqf.headers)

    s2 = urllib.parse.urlparse(redirectURL)
    header["referer"] = redirectURL
    header["cookie"] = reqf.headers["set-cookie"]
    header["authority"] = s2.netloc

    # .replace("-", "%2D")

    # print(dd, [cc])
    headerStr = ""
    for key, value in header.items():
        # print(key+':'+str(value))
        headerStr += key + ":" + str(value) + "\n"

    relativeFolder = ""
    rootFolder = query["id"]
    for i in rootFolder.split("/"):
        if isSharepoint:
            if i != "Shared Documents":
                relativeFolder += i + "/"
            else:
                relativeFolder += i
                break
        else:
            if i != "Documents":
                relativeFolder += i + "/"
            else:
                relativeFolder += i
                break
    relativeUrl = (
        parse.quote(relativeFolder)
        .replace("/", "%2F")
        .replace("_", "%5F")
        .replace("-", "%2D")
    )
    rootFolderUrl = (
        parse.quote(rootFolder)
        .replace("/", "%2F")
        .replace("_", "%5F")
        .replace("-", "%2D")
    )

    graphqlVar = (
        '{"query":"query (\n        $listServerRelativeUrl: String!,$renderListDataAsStreamParameters: RenderListDataAsStreamParameters!,$renderListDataAsStreamQueryString: String!\n        )\n      {\n      \n      legacy {\n      \n      renderListDataAsStream(\n      listServerRelativeUrl: $listServerRelativeUrl,\n      parameters: $renderListDataAsStreamParameters,\n      queryString: $renderListDataAsStreamQueryString\n      )\n    }\n      \n      \n  perf {\n    executionTime\n    overheadTime\n    parsingTime\n    queryCount\n    validationTime\n    resolvers {\n      name\n      queryCount\n      resolveTime\n      waitTime\n    }\n  }\n    }","variables":{"listServerRelativeUrl":"%s","renderListDataAsStreamParameters":{"renderOptions":5707527,"allowMultipleValueFilterForTaxonomyFields":true,"addRequiredFields":true,"folderServerRelativeUrl":"%s"},"renderListDataAsStreamQueryString":"@a1=\'%s\'&RootFolder=%s&TryNewExperienceSingle=TRUE"}}'
        % (relativeFolder, rootFolder, relativeUrl, rootFolderUrl)
    )

    # print(graphqlVar)
    s2 = urllib.parse.urlparse(redirectURL)
    tempHeader = copy.deepcopy(header)
    tempHeader["referer"] = redirectURL
    tempHeader["cookie"] = reqf.headers["set-cookie"]
    tempHeader["authority"] = s2.netloc
    tempHeader["content-type"] = "application/json;odata=verbose"
    # print(redirectSplitURL)

    graphqlReq = req.post(
        "/".join(redirectSplitURL[:-3]) + "/_api/v2.1/graphql",
        data=graphqlVar.encode("utf-8"),
        headers=tempHeader,
    )
    graphqlReq = json.loads(graphqlReq.text)
    # print(graphqlReq)
    if "NextHref" in graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]:
        nextHref = graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"][
            "NextHref"
        ] + "&@a1=%s&TryNewExperienceSingle=TRUE" % ("%27" + relativeUrl + "%27")
        filesData.extend(
            graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"]
        )
        # print(filesData)

        listViewXml = graphqlReq["data"]["legacy"]["renderListDataAsStream"][
            "ViewMetadata"
        ]["ListViewXml"]
        renderListDataAsStreamVar = '{"parameters":{"__metadata":{"type":"SP.RenderListDataParameters"},"RenderOptions":1216519,"ViewXml":"%s","AllowMultipleValueFilterForTaxonomyFields":true,"AddRequiredFields":true}}' % (
            listViewXml
        ).replace(
            '"', '\\"'
        )
        # print(renderListDataAsStreamVar, nextHref,1)

        # print(listViewXml)

        graphqlReq = req.post(
            "/".join(redirectSplitURL[:-3])
            + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream"
            + nextHref,
            data=renderListDataAsStreamVar.encode("utf-8"),
            headers=tempHeader,
        )
        graphqlReq = json.loads(graphqlReq.text)
        # print(graphqlReq)

        while "NextHref" in graphqlReq["ListData"]:
            nextHref = graphqlReq["ListData"][
                "NextHref"
            ] + "&@a1=%s&TryNewExperienceSingle=TRUE" % ("%27" + relativeUrl + "%27")
            filesData.extend(graphqlReq["ListData"]["Row"])
            graphqlReq = req.post(
                "/".join(redirectSplitURL[:-3])
                + "/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream"
                + nextHref,
                data=renderListDataAsStreamVar.encode("utf-8"),
                headers=tempHeader,
            )
            # print(graphqlReq.text)
            graphqlReq = json.loads(graphqlReq.text)
            # print(graphqlReq)
        filesData.extend(graphqlReq["ListData"]["Row"])
    else:
        filesData.extend(
            graphqlReq["data"]["legacy"]["renderListDataAsStream"]["ListData"]["Row"]
        )

    # fileCount = 0
    for i in filesData:
        if i["FSObjType"] == "1":
            print(
                "\t" * layers,
                "Folder(文件夹): ",
                i["FileLeafRef"],
                "\tUnique ID: ",
                i["UniqueId"],
                "Entering(正在进入)",
            )
            _query = query.copy()
            _query["id"] = os.path.join(_query["id"], i["FileLeafRef"]).replace(
                "\\", "/"
            )
            if not isSharepoint:
                originalPath = (
                    "/".join(redirectSplitURL[:-1])
                    + "/onedrive.aspx?"
                    + urllib.parse.urlencode(_query)
                )
            else:
                originalPath = (
                    "/".join(redirectSplitURL[:-1])
                    + "/AllItems.aspx?"
                    + urllib.parse.urlencode(_query)
                )
            downloadFiles(
                originalPath,
                req,
                layers + 1,
                aria2URL,
                token,
                num=num,
                _id=fileCount,
                originalDir=originalDir,
            )
            # fileCount += downloadFiles(originalPath, req, layers+1,
            #                            aria2URL, token, num=num, _id=fileCount, originalDir=originalDir)
        else:
            fileCount += 1
            # print(num)
            if num == [0] or (isinstance(num, list) and fileCount in num):
                print(
                    "\t" * layers,
                    "File(文件) [%d]: %s\tUnique ID: %s\tPushing(正在推送)"
                    % (fileCount, i["FileLeafRef"], i["UniqueId"]),
                )
                cc = downloadURL + (i["UniqueId"][1:-1].lower())
                dd = dict(
                    out=i["FileLeafRef"],
                    header=headerStr,
                    dir=originalDir + str(query["id"]).split("Documents", 1)[1],
                )
                jsonreq = json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": "qwer",
                        "method": "aria2.addUri",
                        "params": ["token:" + token, [cc], dd],
                    }
                )

                c = requests.post(aria2URL, data=jsonreq)
                pprint(json.loads(c.text))
                # exit(0)
            else:
                print(
                    "\t" * layers,
                    "File(文件) [%d]: %s\tUnique ID: %s\tNon target files(非目标文件)"
                    % (fileCount, i["FileLeafRef"], i["UniqueId"]),
                )
    return fileCount


def getFilesHavePwd(originalPath, password):
    req = newSession()
    req.cookies.update(header)
    r = req.get(originalPath)
    p = re.search('SideBySideToken" value="(.*?)" />', r.text)
    SideBySideToken = p.group(1)
    p = re.search('id="__VIEWSTATE" value="(.*?)" />', r.text)
    __VIEWSTATE = p.group(1)
    p = re.search('id="__VIEWSTATEGENERATOR" value="(.*?)" />', r.text)
    __VIEWSTATEGENERATOR = p.group(1)
    p = re.search('__EVENTVALIDATION" value="(.*?)" />', r.text)
    __EVENTVALIDATION = p.group(1)
    s2 = parse.urlparse(originalPath)
    redirectURL = originalPath
    redirectSplitURL = redirectURL.split("/")
    shareQuery = s2.path.split("/")[-1]
    redirectSplitURL[-1] = "guestaccess.aspx?" + s2.query + "&share=" + shareQuery
    pwdURL = "/".join(redirectSplitURL)
    print(pwdURL, r.headers)
    hewHeader = {
        "sec-ch-ua-mobile": "?0",
        "upgrade-insecure-requests": "1",
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "content-type": "application/x-www-form-urlencoded",
        "connection": "keep-alive",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "host": s2.netloc,
        "origin": s2.scheme + "://" + s2.netloc,
        "Referer": originalPath,
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    req.cookies.update(header)
    r = req.post(
        pwdURL,
        data={
            "__EVENTTARGET": "btnSubmitPassword",
            "__EVENTARGUMENT": None,
            "SideBySideToken": SideBySideToken,
            "__VIEWSTATE": __VIEWSTATE,
            "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
            "__VIEWSTATEENCRYPTED": None,
            "__EVENTVALIDATION": __EVENTVALIDATION,
            "txtPassword": password,
        },
        headers=hewHeader,
        allow_redirects=False,
    )
    print(r.headers, r.text)
    new_url = r.headers["Location"]

    r = req.get(new_url, headers=r.headers, allow_redirects=False)
    print(r.headers, r.text)


def wildcardsMatchFiles(text):
    fileNum = []
    data = text.split(",")
    for v in data:
        i = v.split("-")
        if len(i) < 2:
            fileNum.append(int(i[0]))
        else:
            for j in range(int(i[0]), int(i[1]) + 1):
                fileNum.append(j)
    # print(fileNum)
    fileNum = list(set(fileNum))
    return sorted(fileNum)


def getAria2ConfigDir(aria2URL, token):
    jsonreq = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": "qwer",
            "method": "aria2.getGlobalOption",
            "params": ["token:" + token],
        }
    )
    c = requests.post(aria2URL, data=jsonreq)
    return json.loads(c.text)["result"]["dir"]


if __name__ == "__main__":
    args = parse_arguments()
    if args.download:
        downloadFiles(
            args.onedrive_url,
            None,
            0,
            args.aria2_link,
            args.aria2_secret,
            num=wildcardsMatchFiles(args.download_num),
        )
    else:
        getFiles(args.onedrive_url, None, 0)
    #
    # getFilesHavePwd(
    #   "https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r&guestaccesstoken=xyz", "xkx")
