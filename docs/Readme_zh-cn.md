# OneDriveShareLinkPushAria2

从 OneDrive 或 SharePoint 共享链接提取下载 URL 并将其推送到 aria2，即使在无图形界面的系统中依然可以使用。

# 依赖

requests==2.25.1

pyppeteer==0.2.5

# 配置 aria2

## 安装 aria2

macOS 系统:
```bash
brew install aria2
```

Ubuntu/Debian 系统:
```bash
sudo apt-get install aria2
```

CentOS/RHEL 系统:
```bash
sudo yum install aria2
```

Windows 系统:
从 https://aria2.github.io/ 下载并安装 aria2

## 配置 aria2 RPC

启动 aria2 RPC 服务:
```bash
aria2c --enable-rpc --rpc-listen-all=true --rpc-allow-origin-all -D -d <下载目录>
```

# 特点

目前本程序支持的下载方式：

- xxx-my.sharepoint.com 下载链接的下载
  - 无下载密码的多文件推送
  - 有下载密码的多文件推送
  - 嵌套文件夹的文件推送
  - 任意选择文件推送
  - 针对超多文件（超过 30 个）的分享链接，实现了的遍历查看和下载
- xxx.sharepoint.com 下载链接的下载
- xxx-my.sharepoint.cn 下载链接的下载(理论上支持)

**注意：Aria2 本身不支持 HTTP POST 型的下载链接，而 OneDrive 文件夹打包下载为 HTTP POST 型的下载链接，所以本程序将不会支持 OneDrive 文件夹打包下载**

## 输出文件列表

使用以下命令输出文件列表到 list.txt：

```bash
python main.py "https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh" > list.txt
```

使用 powershell 运行此命令可能会输出乱码, 先运行以下命令即可修复

```bash
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

## OneDrive 个人版

截至 2024 年 12 月 13 日，OneDrive 个人版的下载链接为直链，可以打开 F12 后刷新页面，找到 Network(网络)中的`https://my.microsoftpersonalcontent.com/_api/v2.0/drives/{}/items/{}children?%24top=100&orderby=folder%2Cname&%24expand=thumbnails%2Ctags&select=*%2Cocr%2CwebDavUrl%2CsharepointIds%2CisRestricted%2CcommentSettings%2CspecialFolder%2CcontainingDrivePolicyScenarioViewpoint&ump=1`请求 (花括号中的内容会随着不同的文件而改变)，查看返回的 json 数据，找到`@content.downloadUrl`字段，即为下载链接。

或者转到Network中，按下Ctrl + F，输入`@content.downloadUrl`，找到对应的请求，查看返回的数据，找到`@content.downloadUrl`字段，即为下载链接。
![alt text](image.png)


可以查看[test.py](../test.py)文件，里面有一个示例，可以直接运行，获取对应的json数据。

## 无密码的链接

程序现在使用命令行参数。以下是可用的选项：

- OneDrive URL：下载地址（必需参数）
- `--aria2-link`：aria2 的 RPC 地址，默认为 `http://127.0.0.1:6800/jsonrpc`
- `--aria2-secret`：aria2 的密码，默认为空
- `--download`：是否下载，如果不指定则只输出文件列表
- `--download-num`：要下载的文件列表，默认为 "0"（表示全部文件）

如果要下载特定文件，使用 `--download-num` 选项：

- 下载第二个文件：`--download-num "2"`
- 下载第二和第三个文件：`--download-num "2-3"`
- 下载第二、第三、第四、第七个文件：`--download-num "2-4,7"`

使用示例：
```bash
# 仅列出文件
python main.py "你的-onedrive-分享链接"

# 下载所有文件
python main.py "你的-onedrive-分享链接" --download

# 下载指定文件
python main.py "你的-onedrive-分享链接" --download --download-num "2-4,7"

# 使用自定义 aria2 设置
python main.py "你的-onedrive-分享链接" --download --aria2-link "http://localhost:6800/jsonrpc" --aria2-secret "你的密码"
```

## 有密码链接下载

以下载链接为例：
https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r

此时需要使用有密码的下载代码，即 [havepassword.py](../havepassword.py)。打开这个文件，可以看到一些全局变量（重复的不再赘述）：

- OneDriveSharePwd：OneDrive 链接的密码

使用方法与上面类似。

# 注意

使用前，需要使用 `git clone https://github.com/gaowanliang/OneDriveShareLinkPushAria2.git` 将项目整个克隆下来才能使用。havepassword.py 依赖于 main.py，如果要使用需要密码的版本，需要 `pip install pyppeteer`。

此程序基本功能都已实现，之后很长的一段时间内，如果不是软件无法使用了，则不再维护。如有运行问题，请在提出 issue 时带上下载链接，不提供下载链接的 bug 类型的 issue 将不会解决。
