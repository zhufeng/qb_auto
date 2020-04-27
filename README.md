# qb_auto
some qbittorrent automation stuff for Private Tracker.

通过qbittorrent的webui来实现对种子进行自定义自动设置分类的功能。

目前本工具在更新中，README可能有更新不及时的情况，请见谅。

---

## 环境准备
支持win/linux/mac的__python3__环境，在使用前，需要通过pip安装qbittorrent-api模块。
```
pip install qbittorrent-api
pip install torrentool
```

---

## 使用方法
1. 下载本项目的qb.py和qb_auto.ini文件。
2. 编辑qb_auto.ini文件，在[connection]区域内填入qb服务器的地址/端口/用户名/密码。
3. [category]区域里面是预定义的一些PT tracker地址和qb分类的对应关系，一行代表一个tracker。该区域内的部分可以自定义添加，等号左边为tracker地址的关键字，右边是qb定义的分类。注意等号右边的__分类名，必须要已在qb中已存在__，否则运行会报错。
4. [label]区域用于自动设置种子的标签，目前功能还在开发中，待使用。
5. 
6. 
7.
8. qb.py主程序里面定义了很多函数，都写了详细的注释，可以根据需要自行注释或取消main()的函数调用来实现相应的功能。
8. 使用 python3 qb.py 命令运行。
9. 检查qb中种子的分类是否已经被正确设置。


---

## 注意事项
1. qb.py文件中默认是对未分类的种子进行操作的。
2. 如果你需要对所有种子进行重新分类，参考qb.py文件中118-121行，自行注释或注释相应的语句来实现。
3. 种子数量如果很多的情况下，运行时可能会有较长时间卡住，请耐心等候。
4. 当开始对种子进行分类设置时，会同时输出种子名和分类名。
