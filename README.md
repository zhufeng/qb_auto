# qb_auto
some qbittorrent automation stuff for Private Tracker.

通过qbittorrent的webui来实现对种子进行自定义自动设置分类的功能。

---

## 环境准备
支持win/linux/mac的__python3__环境，在使用前，需要通过pip安装qbittorrent-api模块。
```
pip install qbittorrent-api
```

---

## 使用方法
1. 下载本项目的qb.py和qb_categories.txt文件。
2. 在以上两个文件的目录中创建一个qb_auto_ext.txt的文件，__文件名不能错__。
3. qb_auto_ext.txt文件的第一行填入qb webui的地址，例如 http://xxx.com:8085。
4. qb_auto_ext.txt文件的第二行和第三行分别填入qb webui的用户名和密码，__顺序一定不能错__。
5. qb_categories.txt是自定义的种子tracker和qb分类的对应关系表，一行代表一个tracker。
6. 每一行的冒号左边是tracker地址的关键字，冒号右边是qb中已预定义好的分类名，__注意冒号只能是半角__。
7. qb_categories.txt中已经根据我的设置定义好了一些pt站，可按需自行修改对应关系。
8. 注意qb_categories.txt中冒号右边的__分类名，必须要已在qb中已存在__，否则运行会报错。
8. 使用 python3 qb.py 命令运行。
9. 检查qb中种子的分类是否已经被正确设置。


---

## 注意事项
1. qb.py文件中默认是对未分类的种子进行操作的。
2. 如果你需要对所有种子进行重新分类，那么将qb.py文件中69行最前面加上#，68行最前面的#去掉。
3. 种子数量如果很多的情况下，运行时可能会有较长时间卡住，请耐心等候。
4. 当开始对种子进行分类设置时，会同时输出种子名和分类名。
