# qb_auto
some qbittorrent automation stuff via python for Private Tracker.

通过qbittorrent的API，使用python来实现一些在GUI及webui中不太容易实现的功能。如：对种子进行自定义自动设置分类、提取特定状态的种子、按规则重命名torrent种子文件等。

目前本工具在更新中，README可能有更新不及时的情况，请见谅。

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
请输入需要使用的功能选项：(直接回车默认选择1)
```

1. qb.py为主程序。
2. qb_auto.ini为配置文件，主要用于自定义qb中的“分类”，它将种子的tracker地址的关键字和qb分类一一对应。


## 使用方法
1. 下载本项目的qb.py和qb_auto.ini文件。
2. 编辑qb_auto.ini文件，该文件主要需要修改[connection]和[category]这两块的内容。
3. 在[connection]区域内填入qb webui的地址/端口/用户名/密码，**不需要在最前面加http://**。
4. 在[category]区域内已经预填了一些常见pt tracker地址和qb分类的对应关系，一行代表一个tracker。该区域内的部分可以自定义添加或修改，**等号左边为tracker地址的关键字**，右边是qb定义的分类名。注意等号右边的**分类名，必须要已在qb中已存在**，否则运行会报错。
5. [label]区域用于自动设置种子的标签，目前功能还在开发中，待使用。
6. qb.py主程序里面定义了很多函数，都写了详细的注释，可以根据需要自行注释或取消main()的函数调用来实现相应的功能。
7. 使用 python3 qb.py 命令运行。
8. 检查qb中种子的分类是否已经被正确设置，或其它功能已实现。


---

## 注意事项
1. qb的种子数量很多的情况下(>1000)，运行时可能会有较长时间卡住，请耐心等候。
2. 当开始对种子进行分类设置时，会同时输出种子名和分类名。


---

README.md 更新日期：20/10/3 16:14 
