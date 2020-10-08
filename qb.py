import os
import re
import uuid
import time
import shutil
import datetime
import telnetlib
import configparser
import qbittorrentapi
from torrentool.api import Torrent
from torrentool.api import Bencode


# 读取配置文件[连接/分类/标签信息]
def readConf():
    print ("I'm readConf()...");

    global host;
    global port;
    global user;
    global passwd;
    global cateDict;
    global labelDict;

    # 修复configparser读取文件时左边总为小写
    cfg = configparser.RawConfigParser();
    cfg.optionxform = str;

    # 适配.gitignore防止自用登录信息被git push泄露
    if os.path.exists('qb_auto1.ini'):
        cfg.read_file(open("qb_auto1.ini"));
        print ("Reading qb_auto1.ini...");
    else:
        cfg.read_file(open("qb_auto.ini"));
        print ("Reading qb_auto.ini...");
    # print (cfg.sections());

    # 读取配置文件中qb webui[connection]登录信息部分
    port = cfg['connection']['port'];
    # print (str.isdigit(port));
    if str.isdigit(port):
        pass;
        # print (port);
    else:
        print ("Port is NOT defined or Illegal!!! Terminated!!!\n");
        exit();

    # 判断localhost:port是否可连接，可连接则使用localhost
    # 否则使用qb_auto.ini中定义的host
    try:
        if telnetlib.Telnet().open('127.0.0.1', port) is None:
            host = 'http://localhost';
            # print ("Using: localhost:" + port + "...");
    except Exception as e:
        host = "http://" + cfg['connection']['host'];
        # if len(host) == 0:
        if str.isdigit(host) or len(host) == 0:
            print ("Host is NOT defined or Illegal!!! Terminated!!!\n");
            exit();
        else:
            pass;
            # print ("Telnet -> localhost:" + port + " FAILED!!!");
            # print ("Using predefined host: " + host);

    user = cfg['connection']['user'];
    passwd = cfg['connection']['password'];
    if len(user) == 0 or len(passwd) == 0:
        print ("User or Password is NOT defined !!! Terminated!!!\n");
        exit();

    # 输入打码
    user1 = user[0:3] + "***" + user[len(user)-3:];
    host1 = host[7:11] + "***" + host[len(host)-5:len(host)];
    port1 = port[0:1] + "***" + port[len(port)-2:len(port)];
    # print ("Using: " + user + "@" + host + ":" + port + "....");
    print ("Using: " + user1 + "@" + host1 + ":" + port1 + "....");

    # 读取配置文件中[category]分类部分
    cateDict = cfg._sections['category'];
    # print (cateDict);

    # 读取配置文件中[label]标签部分
    labelDict = cfg._sections['label'];
    # print (labelDict);

    print ("readConf done!...\n");


# 连接到qb webui
def qbConn(host,port,user,passwd):
    print ("I'm qbConn()...");

    global qbClient;
    host = host + ":" + port;
    # print (host);

    # instantiate a Client using the appropriate WebUI configuration
    # qbClient = qbittorrentapi.Client(host='localhost:****', username='***', password='***')
    qbClient = qbittorrentapi.Client(host=host, username=user, password=passwd);

    # the Client will automatically acquire/maintain a logged in state in line with any request.
    # therefore, this is not necessary; however, you many want to test the provided login credentials.
    try:
        qbClient.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        print(e);

    # display qBittorrent info
    print(f'qBittorrent: {qbClient.app.version}');
    print(f'qBittorrent Web API: {qbClient.app.web_api_version}');
    # for k,v in qbClient.app.build_info.items():
        # print(f'{k}: {v}');

    # retrieve and show all torrents
    # for torrent in qbClient.torrents_info():
        # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

    # pause all torrents 
    # # # # # qbClient.torrents.pause.all()

    # print (qbClient.torrents_info(status_filter='active'));

    print ("qbConn done!...\n");


# 使用读取到的配置文件分类信息对种子进行自动设置分类
def autoCate(qbClient, cateDict):
    print ("I'm autoCate()...");

    # category=''表示未分类种子，不加任何参数表示选中所有种子
    torrents = qbClient.torrents_info(category='');
    # torrents = qbClient.torrents_info(category='frds');
    # torrents = qbClient.torrents_info();

    if len(torrents) == 0:
        print ("No Uncategoried torrent !! Terminated!!\n");
        # exit();
        return;

    for torrent in torrents:
        # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')
        # print (torrent);
        for tracker in torrent.trackers:
            trackerUrl = tracker.url[0:30];
            if (trackerUrl.startswith('http')):
                # print (trackerUrl);
                # print (torrent.name);
                for k,v in cateDict.items():
                    # print (k);
                    if re.search(k, trackerUrl):
                        # print (v)
                        torrent.set_category(category=v);
                        # print ("Category SET!! -> " + torrent.name[0:30]);
                        print (torrent.name[0:30] + " -> " + v );

    print ("AutoCate done...!\n");


# 使用读取到的配置文件标签信息对种子进行自动设置标签
def autoLabel(qbClient, labelDict, cate=None):
    print ("I'm autoLabel()...");

    # 强制对所有种子设置标签
    if cate is None:
        print ("AutoLabel ALL torrents...");
        torrents = qbClient.torrents_info();
    # 强制对传入分类名的种子设置标签
    else:
        torrents = qbClient.torrents_info(category=cate);


    # torrents = qbClient.torrents_info(category='');
    # torrents = qbClient.torrents_info(category='frds');
    # torrents = qbClient.torrents_info(category='frds',limit=100);
    # torrents = qbClient.torrents_info();

    # print (torrents);

    for torrent in torrents:
        # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')
        torrentName = torrent.name;
        torrentCate = torrent.category;
        torrentHash = torrent.hash;
        # print (torrentName);
        # print (torrentCate);
        print ("11 " + torrentHash);
        for k,v in labelDict.items():
            # print (k);
            if re.search(k, torrentName):
                # print (v)
                print (torrentHash);
                # torrent.addTags(hashes=torrentHash, tags=v);
                print (torrent.name[0:30] + " -> " + v );
            else:
                print ("No " + v + " like torrent!!");
                pass;

    print ("AutoLabel done...!\n");


# 强制重新汇报所有种子或某个分类的种子
def forceReannounce(qbClient, cate=None):
    print ("I'm ForceReannounce()...");

    # 强制重新汇报所有种子
    if cate is None:
        print ("Reannoucing ALL torrents...");
        qbClient.torrents_reannounce(hashes='all');
        print ("ForceReannounce ALL torrents done...!\n");
    # 强制汇报传入分类名的种子
    else:
        print ("[" + cate + "] torrents Reannoucing...");
        torrents = qbClient.torrents_info(category=cate);
        for torrent in torrents:
            # print ("[" + torrent.hash + "] " + torrent.name[:30]);
            hash = torrent.hash;
            qbClient.torrents_reannounce(hashes=hash);
        print ("[" + cate + "] ForceReannounce done...!\n");
    print ("forceReannounce done!...\n");


# 对种子的文件内容进行简单地文件存在检查
def checkFileExistence():
    pass;


# 按tracker来重命名种子文件
def renameTorrent(path, cate=None, type='first'):

    print ("I'm renameTorrent()...");
    print ("Renaming type is -> " + type);

    # 判断path参数的文件夹是否存在, 不存在就退出
    if os.path.exists(path):
        print (path + " exists...");
    else:
        print (path + " not exists!!! Terminating ...");
        exit();

    winerror = [];
    for file in os.listdir(path):
        if os.path.isfile( path + file) & file.endswith('.torrent'):
            print ( path + file);

            torrent_metadata = Bencode.read_file( path + file );
            torrent_tracker = torrent_metadata['announce'][0:50];
            torrent_name = torrent_metadata['info']['name'];
            if ( "private" in torrent_metadata['info'].keys() ):
                torrent_is_private = torrent_metadata['info']['private'];
            else:
                print ("!!!!!");
                print ("Torrent don't have PRIVATE attribute...");
                print ("!!!!!");
                torrent_is_private = 0;
            # print (torrent_metadata['info'].keys());
            # print (torrent_tracker);
            # print (torrent_name + '\n');

            for k,v in cateDict.items():
                # print (k);
                # if re.search(k, torrent_tracker.decode()):
                if re.search(k, torrent_tracker):
                    # print (v)

                    # 增加随机UUID，防止重命名文件时失败
                    uid = uuid.uuid1().hex[0:8];
                    uid = '_' + uid + '_';

                    file_site_first = '[' + v + ']_' + torrent_name + uid + '.torrent';
                    file_site_last = torrent_name + uid + '[' + v + ']' + '.torrent';

                    # print (file_site_first);
                    # print (file_site_last);

                    if (type == 'first'):
                        file_new = file_site_first;
                    else:
                        file_new = file_site_last;

                    # 切换命名方法
                    # file_new = file_site_first;
                    # file_new = file_site_last;

                    try:
                        if os.path.join(path, file_new) == os.path.join(path, file):
                            print (file);
                            print ("No need to Rename...\n");
                            pass;
                        else:
                            print (file + " Renaming -> \n" + file_new );
                            os.rename(os.path.join(path, file),os.path.join(path, file_new));
                            print ("");
                    except WindowsError:
                        pass;
                        # winerror.append(file)
    print ("renameTorrent done...!\n");


# 复制qb暂停种子的torrent文件到特定目录
def copyPausedTorrentFile(qbClient, path, qb_path, cateDict=None):

    print ("I'm copyPausedTorrentFile()...");

    # 判断path参数的文件夹是否存在, 不存在就创建
    if os.path.exists(path):
        print (path + " exists...");
    else:
        print (path + " not exists!!! Creating it ...");
        os.mkdir(path);

    torrents = qbClient.torrents_info(filter='paused');
    # torrents = qbClient.torrents_info(category='');

    winerror = [];
    for torrent in torrents:
        # print(f'{torrent.hash}: {torrent.name[0:30]} ({torrent.state})')
        # print (torrent.hash + "|" + torrent.name[0:30] + "|" + torrent.save_path);

        print ("Copying " + torrent.hash + " to " + path + "...");
        torrent_file = qb_path + torrent.hash + ".torrent";
        # print (torrent_file);

        # 从qb BT_backup目录复制筛选出来的种子到path目录
        shutil.copy(torrent_file, path);

    print ("copyPausedTorrentFile done...!\n");


# 获取特定种子的信息
def getTorrentInfo(qbClient, cateDict=None):

    print ("I'm getTorrentInfo()...");

    # 筛选状态为"paused 暂停"的种子
    torrents = qbClient.torrents_info(filter='paused');

    # 筛选分类为"cmct"的种子
    # torrents = qbClient.torrents_info(category='cmct');

    winerror = [];
    for torrent in torrents:

        ## qb官方 torrent list的属性 
        ## https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-torrent-list

        # 获取种子hash/种子名/种子状态
        # print(f'{torrent.hash}|{torrent.name[0:30]}|{torrent.state}|{torrent.save_path}');

        ## qb官方 torrent properties属性 
        ## https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-torrent-generic-properties

        # 查询种子属性需要使用种子hash作为参数传入
        # 获取种子总大小等属性
        torrentProperties = qbClient.torrents_properties(torrent_hash = torrent.hash);
        print (f'{torrent.hash}|{torrent.name[0:30]}|{torrentProperties.total_size}|{torrent.save_path}');

    print ("getTorrentInfo done...!\n");


def main():
    print ("I'm main()...", "\n");

    global host;
    global port;
    global user;
    global passwd;
    global cateDict;
    global labelDict;
    global qbClient;
    global torrents;

    # 接收输入选项前先读取qb_auto.ini配置文件
    readConf();
    # print (host,user,passwd);
    # print (cateDict);
    # print (labelDict);

    print ("    * * * *  功 能 菜 单  * * * *    \n");
    print ("1. 将qb未分类种子按预定义规则进行分类。");
    print ("2. 重命名特定目录下的torrent种子文件。");
    print ("3. 将qb暂停的种子的torrent文件复制到特定目录并重命名。");
    print ("4. 获取qb特定种子的信息。");
    print ("请输入需要使用的功能选项：(直接回车默认选择1) \n");

    # 定义存放torrent的工作目录及qb BT_backup路径
    path = r'E:/torrents/';
    qb_path = r'D:/常用软件/qbittorrent_x64/profile/qBittorrent/data/BT_backup/';

    # 获取输入值判断执行什么功能函数
    option = input("");
    # print (option);

    if option == "" or option == "1":
        # print ("输入为空");

        # 连接qb webapi
        qbConn(host, port, user, passwd);

        # 强制重新汇报所有种子
        # forceReannounce(qbClient,'frds');
        forceReannounce(qbClient);

        # 自动对未分类种子进行分类
        autoCate(qbClient, cateDict);
        # print ("Hahaha -> 直接回车或1");

    elif option == "2":
        print ("请输入需要重命名的种子的路径：(直接回车默认使用E:/torrents/)");
        path = input("");
        if path == "":
            print ("输入path路径为空, 使用E:/torrents/...");
            path = r'E:/torrents/';
            pass;

        print ("请输入种子的pt站名位置: (直接回车默认为站名在前,其它任何字符为默认在后)");
        type = input("");
        if type == "":
            # print ("first");
            # print (path);
            renameTorrent(path);
        else:
            # print ("last");
            # print (path);
            renameTorrent(path, type='last');

    elif option == "3":
        # 连接qb webapi
        qbConn(host, port, user, passwd);

        print ("请输入需要重命名的种子的路径：(直接回车默认使用E:/torrents/)");
        path = input("");
        if path == "":
            print ("输入path路径为空, 使用E:/torrents/...");
            path = r'E:/torrents/';
            pass;

        print ("请输入种子的pt站名位置: (直接回车默认为站名在前,其它任何字符为默认在后)");
        type = input("");

        copyPausedTorrentFile(qbClient, path, qb_path);

        if type == "":
            print ("first");
            # renameTorrent(path);
        else:
            print ("last");
            # renameTorrent(path, type='last');

    elif option == "4":
        # 连接qb webapi
        qbConn(host, port, user, passwd);
        getTorrentInfo(qbClient, cateDict=None);



    # autoLabel(qbClient, labelDict);



if __name__ == '__main__':
    main();

