# qb_auto
some qbittorrent automation stuff via python for Private Tracker.

通过qbittorrent的API，使用python来实现一些在GUI及webui中不太容易实现的功能。如：对种子进行自定义自动设置分类、提取特定状态的种子、按规则重命名torrent种子文件等。

本工具会随着使用中发现的问题或需求不定期更新，README可能有更新不及时的情况，请参见commit备注。

---

## 环境准备
支持win/linux/mac的 **python3** 环境，在使用前，需要通过pip安装qbittorrent-api等模块，如运行时提示缺包，请自行使用pip安装即可。
本工具理论上支持各平台的qbittorrent，但目前仅在**windows平台的qb**做过测试，在其它平台上使用可能需要对代码做少量修改，请自行测试。
```
pip install qbittorrent-api
pip install torrentool
```

---

## 功能介绍及说明
使用python运行qb.py之后，将会出现如下的目前已实现的功能的菜单供选择，按提示使用即可。

```
    * * * *  功 能 菜 单  * * * *

1. 将qb未分类种子按预定义规则进行分类。
2. 重命名特定目录下的torrent种子文件。
3. 将qb暂停的种子的torrent文件复制到特定目录并重命名。
4. 获取qb特定种子的信息。
5. 对qb中tracker为http的种子修改为https。
请输入需要使用的功能选项：(直接回车默认选择1)

```

1. qb.py为主程序。
2. qb_auto.ini为配置文件，主要用于自定义qb中的“分类”，它将种子的tracker地址的关键字和qb分类一一对应。


## 使用方法
1. 下载本项目的qb.py和qb_auto.ini文件。
2. 编辑qb_auto.ini文件，该文件主要需要修改[connection]和[category]这两块的内容。
3. 在[connection]区域内填入qb webui的地址/端口/用户名/密码，<font color=red>**注意必须要在链接最前面加http://或https://**</font>，默认情况下会忽略https证书错误。
4. 为提高连接性能，默认情况下程序会根据[connection]中定义的端口，首先尝试以localhost:port方式进行连接，如果同端口无法连接则会继续使用定义的host进行连接。
5. [connction]中的upspeed用于设置全局目标上传速度(kb/s)，当全局上传速度小于该值时，会自动对当前活动且限速的种子解除限速。
6. 程序支持定义多个[connection]区域以依次连接多个qb webui地址，但必须以[connection]开头，如[connection1]、[connection2]。
7. 在[category]区域内已经预填了一些常见pt tracker地址和qb分类的对应关系，一行代表一个tracker。该区域内的部分可以自定义添加或修改，**等号左边为tracker地址的关键字**，右边是qb定义的分类名。注意等号右边的**分类名，必须要已在qb中已存在**，否则运行会报错。
8. [label]区域用于自动设置种子的标签，目前功能还在开发中，待使用。
9. qb.py主程序里面定义了很多函数，都写了详细的注释，可以根据需要自行注释或取消main()的函数调用来实现相应的功能。
10. 使用 python3 qb.py 命令运行。
11. 检查qb中种子的分类是否已经被正确设置，或其它功能已实现。


---

## 注意事项
1. qb的种子数量较多的情况下(>1000)，运行时可能会有较长时间卡住，请耐心等候。
2. 当开始对种子进行分类设置时，会同时输出种子名和分类名。


---

README.md 更新日期：

Tue Jan 25 15:28:45 CST 2022
