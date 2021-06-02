# OneDriveShareLinkPushAria2
Extract the download URL from OneDrive or SharePoint share link and push it to aria2

从OneDrive或SharePoint共享链接提取下载URL并将其推送到aria2

# 使用方法

目前本程序支持的下载方式：
* xxx-my.sharepoint.com 下载链接的下载
  * 无下载密码的多文件推送
  * 有下载密码的多文件推送
  * 嵌套文件夹的文件推送
  * 任意选择文件推送
* xxx-my.sharepoint.cn 下载链接的下载(理论上支持)

## 无密码的链接

以 https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh 这个下载链接为例

此时需要使用无密码的下载代码，也就是[main.py](main.py)，打开这个文件，可以看到有一些全局变量：
* OneDriveShareURL: 下载地址，此处应该填写 https://gitaccuacnz2-my.sharepoint.com/:f:/g/personal/mail_finderacg_com/EheQwACFhe9JuGUn4hlg9esBsKyk5jp9-Iz69kqzLLF5Xw?e=FG7SHh
* aria2Link: aria2 的rpc地址，如果是本机，一般是 `http://localhost:端口号/jsonrpc`
* aria2Secret: aria2 的密码
* isDownload: 是否下载，如果是`False`，只输出文件列表
* downloadStart: 下载起始文件的号码，默认为1
* downloadNum: 从downloadStart开始的文件连续下载多少个，-1表示全部下载（-1时，无视downloadStart）

如果想要下载第二个文件，则需要`downloadStart=2`，`downloadNum=1`

如果想要下载第二、第三个文件，则需要`downloadStart=2`，`downloadNum=2`

修改好后，确保目标aria2处于开启状态，执行`python3 main.py`

## 有密码的链接
以 https://jia666-my.sharepoint.com/:f:/g/personal/1025_xkx_me/EsqNMFlDoyZKt-RGcsI1F2EB6AiQMBIpQM4Ka247KkyOQw?e=oC1y7r 这个下载链接为例

此时需要使用有密码的下载代码，也就是[havepassword.py](havepassword.py)，打开这个文件，可以看到有一些全局变量（重复的不再赘述）：
* OneDriveSharePwd: OneDrive链接的密码
  
使用方法和上面类似。
