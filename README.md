# 郑州大学健康上报脚本
该脚本仅用于自动打卡郑州大学健康状况上报平台。

## 有什么特点？
拿来主义，分本不用本地化。<br>
直接在GitHub上就能轻松部署<br>
’懒人式‘一次部署，60天无忧打卡（下次再另外部署即可）<br>

## 环境依赖
+ `python==3.7`
+ 用于发送http请求的`requests`模块


## 设置
本项目使用GitHub提供的Actions进行定时打卡，这样**自己就不需要服务器了，直接白嫖GitHub的”服务器“多香啊！！！**<br>
项目已测试成功，能通过Actions直接定时每天打卡，香的一批<br>
最关键的是，GitHub支持了对密码账户等信息的封装，这样可以**保护使用者的信息安全，不被外泄。**<br>

## 用法：
首先将本项目**Fork（右上角）** 到自己的账户下
然后点击项目上方的一行任务栏**Settings（最后一个）**

### 1. Fork 仓库
   * 点击页面右上角的`Fork`按钮，将本项目保存到自己的仓库。点击`Fork`左侧的`Star`键可以表示您对本项目和作者的认同。🤩
   ![fork.PNG](https://i.loli.net/2020/11/24/2hTtGldiZF9B7DX.png)
### 2. 添加 secrets
   * 点击`Settings`-->`Secrets`-->`New repository secret`，进入新建页面。
   ![secrets.PNG](https://i.loli.net/2020/11/24/mIWLRTzUJxuiMHa.png)
   * 在`Name`栏输入`UID`，`Value`栏输入自己的学号，然后点击`Add secret`。
   * 再次点击`Settings`-->`Secrets`-->`New repository secret`，进入新建页面。
   * 在`Name`栏输入`UPW`，`Value`栏输入自己的登录密码，然后点击`Add secret`。
   * 多人模式与单人模式的添加方法相同，具体格式为`学号,学号,学号`和`密码,密码,密码`，例如：`201884160000,201884160001`和`12345678,12345678`(**注意：逗号为英文标点，使用中文标点会导致脚本运行失败**)。
### 3.启用 Actions
   * 点击上方的`Actions`，点击绿色按钮确认启用`Actions`功能。
   * 点击左侧`ZZU COMMUTE HELPER`，点击`Run workflow`，运行一次项目。
   ![actions.PNG](https://i.loli.net/2020/11/24/HrQoCwFkgcAYjps.png)

项目部署完毕后，可以在`Actions`页面点击`View workflow file`查看结果。
![check.PNG](https://i.loli.net/2020/11/24/GUEgdrmpIAxlPW5.png)
如有疑问可通过`Issues`功能提交问题，如出现签到失败的问题请耐心等待更新。

---
## 📢更新方法
   * 点击`Settings`-->`Options`-->`Dangerous Zone`-->`delete this reposity`，按照提示删除本项目，然后重新部署。
   * 使用git，相关命令请自行搜索。
