# OneDriveShareLinkPushAria2
Extract download URLs from OneDrive or SharePoint share links and push them to aria2, even on systems without a GUI.

从OneDrive或SharePoint共享链接提取下载URL并将其推送到aria2，即使在无图形界面的系统中依然可以使用。

# Dependent / 依赖

requests==2.25.1

pyppeteer==0.2.5

# Usage method / 使用方法

At present, this program supports the following download methods:

* xxx-my.sharepoint.com Download of share links
  * Downloading multiple files without password for shared links
  * Downloading multiple files with password for shared links
  * Download of files in nested folders
  * Download any file of your choice
* xxx.sharepoint.com Downloads with share links
* xxx-my.sharepoint.cn Download of share links (theoretically supported)

****

目前本程序支持的下载方式：
* xxx-my.sharepoint.com 下载链接的下载
  * 无下载密码的多文件推送
  * 有下载密码的多文件推送
  * 嵌套文件夹的文件推送
  * 任意选择文件推送
* xxx.sharepoint.com 下载链接的下载
* xxx-my.sharepoint.cn 下载链接的下载(理论上支持)

## Without password for shared links / 无密码的链接

Take this download link as an example:

https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh

At this time, you need to use the download code for no password link, that is, [main.py](main.py). Open this file and you can see that there are some global variables:
* OneDriveShareURL: The download address, which should be filled in here https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh
* aria2Link: aria2's rpc address, usually `http://localhost:Port/jsonrpc` if it's native
* aria2Secret: the password of aria2
* isDownload: whether to download or not, if `False`, only the file list is output
* downloadStart: the number of the starting file to download, default is 1
* downloadNum: the number of consecutive downloads of the file starting from downloadStart, -1 means all of them (when -1, downloadStart is ignored)

If you want to download the second file, you need `downloadNum="2"`

If you want to download the second and third file, you need `downloadNum="2-3"`

If you want to download the second, third, fourth, seventh file, you need `downloadNum="2-4,7"`

and so on.

After modifying, make sure the target aria2 is on and execute `python3 main.py`

****

以 https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh 这个下载链接为例

此时需要使用无密码的下载代码，也就是[main.py](main.py)，打开这个文件，可以看到有一些全局变量：
* OneDriveShareURL: 下载地址，此处应该填写 https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh
* aria2Link: aria2 的rpc地址，如果是本机，一般是 `http://localhost:端口号/jsonrpc`
* aria2Secret: aria2 的密码
* isDownload: 是否下载，如果是`False`，只输出文件列表
* downloadNum: 要下载的文件列表，-1表示全部下载

如果想要下载第二个文件，则需要`downloadNum="2"`

如果想要下载第二、第三个文件，则需要`downloadNum="2-3"`

如果想要下载第二、第三、第四、第七个文件，则需要`downloadNum="2-4,7"`

以此类推

修改好后，确保目标aria2处于开启状态，执行`python3 main.py`

## With password for shared links / 有密码的链接

Take this download link as an example:

https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r

At this time, you need to use the download code for have password link, that is, [havepassword.py](havepassword.py). Open this file and you can see that there are some global variables (repeated without further ado):
* OneDriveSharePwd: Password for the OneDrive link
  
Usage is similar to the above.

****

以 https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r 这个下载链接为例

此时需要使用有密码的下载代码，也就是[havepassword.py](havepassword.py)，打开这个文件，可以看到有一些全局变量（重复的不再赘述）：
* OneDriveSharePwd: OneDrive链接的密码
  
使用方法和上面类似。

# Note
Before you use it, clone the whole project with `git clone https://github.com/gaowanliang/OneDriveShareLinkPushAria2.git` to use it. havepassword.py depends on main.py, if you want to use the version that requires a password If you want to use a version that requires a password, you need to `pip install pyppeteer`


# 注意
使用前，使用 `git clone https://github.com/gaowanliang/OneDriveShareLinkPushAria2.git` 将项目整个克隆，才能使用，havepassword.py依赖于main.py，如果要使用需要密码的版本，需要 `pip install pyppeteer`