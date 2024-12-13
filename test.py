import json
import re
import urllib
import urllib.request

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

OneDriveShareURL = "https://1drv.ms/f/c/5973e13d37fc66d0/EucPv2vQu4ZBq2FNh_Ara-kBpou6yfkbtePq3JFgq8oGgg?e=4KWQP1"

aria2Link = "http://127.0.0.1:6800/jsonrpc"
aria2Secret = ""

isDownload = False
downloadNum = "0"  # 1,2-4,5

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


# 首字母大写
def capitalize(s):
    return s[0].upper() + s[1:]


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
    print(redirectURL)
    rex = re.compile(r"&redeem=(.*)&")
    redeem = rex.search(redirectURL).group(1)

    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(redirectURL).query))
    redirectSplitURL = redirectURL.split("/")
    appid = "1141147648"
    appUuid = "5cbed6ac-a083-4e14-b191-b4ba07653de2"

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

    reqf = req.post("https://api-badgerp.svc.ms/v1.0/token", data={"appId": appUuid})

    deviceCode = "5c872a7a-0906-4ccc-a157-2b003598569f"  # 随机生成

    print(reqf.text)
    authData = json.loads(reqf.text)
    drives = relativeFolder.split("!")[0]
    postData = """--{}
Content-Disposition: form-data;name=data
Prefer: HonorNonIndexedQueriesWarningMayFailRandomly, allowthrottleablequeries, Include-Feature=AddToOneDrive;Vault
X-ClientService-ClientTag: ODC Web
Application: ODC Web
Scenario: BrowseFiles
ScenarioType: AUO
X-HTTP-Method-Override: GET
Content-Type: application/json
Authorization: {} {}


--{}--""".format(
        deviceCode, authData["authScheme"], authData["token"], deviceCode
    ).replace(
        "\n", "\r\n"
    )

    authHeaderRaw = [
        {"name": "Accept", "value": "*/*"},
        {"name": "Accept-Encoding", "value": "gzip, deflate, br, zstd"},
        {"name": "Accept-Language", "value": "zh-HK,zh-TW;q=0.5"},
        {"name": "Connection", "value": "keep-alive"},
        {
            "name": "Content-Type",
            "value": "multipart/form-data;boundary={}".format(deviceCode),
        },
        {"name": "Host", "value": "my.microsoftpersonalcontent.com"},
        {"name": "Origin", "value": "https://onedrive.live.com"},
        {"name": "Referer", "value": "https://onedrive.live.com/"},
        {"name": "Sec-Fetch-Dest", "value": "empty"},
        {"name": "Sec-Fetch-Mode", "value": "cors"},
        {"name": "Sec-Fetch-Site", "value": "cross-site"},
        {"name": "TE", "value": "trailers"},
        {
            "name": "User-Agent",
            "value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
        },
    ]

    authHeader = header
    # 将authHeaderRaw解析成正常的Header
    for i in authHeaderRaw:
        authHeader[i["name"]] = i["value"]

    reqUrl = "https://my.microsoftpersonalcontent.com/_api/v2.0/shares/u!{}/driveitem?%24select=id%2CparentReference".format(
        redeem
    )
    print(reqUrl)
    authDriverHeader = authHeader
    authDriverHeader["Authorization"] = "{} {}".format(
        capitalize(authData["authScheme"]), authData["token"]
    )
    authDriverHeader["Prefer"] = "autoredeem"
    reqf = req.post(
        reqUrl,
        data="%24select=id%2CparentReference",
        headers=authHeader,
    )
    print("ok")

    reqUrl = "https://my.microsoftpersonalcontent.com/_api/v2.0/drives/{}/items/{}children?%24top=100&orderby=folder%2Cname&%24expand=thumbnails%2Ctags&select=*%2Cocr%2CwebDavUrl%2CsharepointIds%2CisRestricted%2CcommentSettings%2CspecialFolder%2CcontainingDrivePolicyScenarioViewpoint&ump=1".format(
        drives.lower(), relativeFolder
    )

    print(reqUrl)
    reqf = req.post(
        reqUrl,
        data=postData.encode("utf-8"),
        headers=authHeader,
    )

    print(reqf.text)

    return 0

    graphqlVar = (
        '{"query":"query (\n        $listServerRelativeUrl: String!,$renderListDataAsStreamParameters: RenderListDataAsStreamParameters!,$renderListDataAsStreamQueryString: String!\n        )\n      {\n      \n      legacy {\n      \n      renderListDataAsStream(\n      listServerRelativeUrl: $listServerRelativeUrl,\n      parameters: $renderListDataAsStreamParameters,\n      queryString: $renderListDataAsStreamQueryString\n      )\n    }\n      \n      \n  perf {\n    executionTime\n    overheadTime\n    parsingTime\n    queryCount\n    validationTime\n    resolvers {\n      name\n      queryCount\n      resolveTime\n      waitTime\n    }\n  }\n    }","variables":{"listServerRelativeUrl":"%s","renderListDataAsStreamParameters":{"renderOptions":5707527,"allowMultipleValueFilterForTaxonomyFields":true,"addRequiredFields":true,"folderServerRelativeUrl":"%s"},"renderListDataAsStreamQueryString":"@a1=\'%s\'&RootFolder=%s&TryNewExperienceSingle=TRUE"}}'
        % (relativeFolder, rootFolder, relativeUrl, rootFolderUrl)
    )

    print(graphqlVar, reqf.headers)
    s2 = urllib.parse.urlparse(redirectURL)
    tempHeader = copy.deepcopy(header)
    tempHeader["referer"] = redirectURL
    if "set-cookie" in reqf.headers:
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


getFiles(OneDriveShareURL, None, 0)
