import os
import re
import sys
import ssl
import uuid
import json
import time
import shutil
import requests
import datetime
import telnetlib
import configparser
import qbittorrentapi
from torrentool.api import Torrent
from torrentool.api import Bencode


# 读取配置文件[连接/分类/标签信息]
def readConf():
    print ("I'm readConf()...");

    global hostDict;
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

    # ini配置文件允许定义多个qb服务器
    # 遍历ini配置文件中带有connection的section
    # 并将它存入hostDict列表中
    # 多个qb host必须以[connection]开头，可以后面接数字
    # 如[connection1] [connection2]等
    hostDict = [];
    for i,elem in enumerate(cfg.sections()):
        # sections里面有以connection开头的部分
        if 'connection' in elem:
            # print (json.dumps(elem,indent=4));
            hostDict.append(cfg._sections[elem]);

            # 判断ini配置中是否存在必需配置项
            if (cfg.has_option(elem,'host')) and (cfg.has_option(elem,'port')) and\
                (cfg.has_option(elem,'user')) and (cfg.has_option(elem,'password')) and\
                (cfg.has_option(elem,'upspeed')):
                pass;
            else:
                print (elem + " : cfg file has NO HOST/PORT/USER/PASSWD/UPSPEED Defined!!! Terminated!!!\n");
                exit();

            # 判断配置文件中host/user/password/upspeed是否合法
            if len(cfg[elem]['host']) == 0 or len(cfg[elem]['user']) == 0 or\
                    len(cfg[elem]['password']) == 0 or len(cfg[elem]['upspeed']) == 0:
                print (elem + " : HOST/USER/PASSWORD/UPSPEED is EMPTY!!! Terminated!!!\n");
                exit();

            # 判断配置文件中port是否为数字
            if str.isdigit(hostDict[i]['port']):
                pass;
            else:
                print (elem + " : Port is NOT defined or Illegal!!! Terminated!!!\n");
                exit();

            # print ("end... " + elem);


    # 读取配置文件中[category]分类部分
    cateDict = cfg._sections['category'];
    # print (json.dumps(cateDict,indent=4));

    # 读取配置文件中[label]标签部分
    labelDict = cfg._sections['label'];
    # print (json.dumps(labelDict,indent=4));

    print ("readConf done!...\n");


# 连接到qb webui
def qbConn(host,port,user,passwd):
    print ("I'm qbConn()...");

    global qbClient;
    global isLocal;
    isLocal = "0";

    # 打码输出读取的配置文件关键信息
    user1 = user[0:3] + "***" + user[len(user)-3:];
    host1 = host[7:11] + "***" + host[len(host)-5:len(host)];
    port1 = port[0:1] + "***" + port[len(port)-2:len(port)];
    conn1 = user1 + "@" + host1 + ":" + port1;
    print ("Using: " + conn1 + "....");

    # 为提高效率，首先判断localhost:port是否可连接
    # 可连接则使用localhost不通过内网转发或ddns
    qblocal = "https://localhost:" + port;
    try:
        r = requests.get(qblocal,verify=False);
        # http get 状态200表示可连接
        if (r.status_code == 200):
            host = "https://localhost";
            isLocal = "1";
            print ("qb localhost connection detected --- Using localhost... ");
    except requests.exceptions.RequestException as e:
        print ("qb localhost Connection Refused!!! " );
        pass;

    # 判断配置文件传入的地址端口是否能正常连接qb
    hostTmp = host + ":" + port;
    try:
        r = requests.get(hostTmp,verify=False,timeout=5);
        if (r.status_code == 200):
            # print (hostTmp + " connected...");
            pass;
    except requests.exceptions.RequestException as e:
        print (conn1 + " NOT able to connect... Skip... \n");
        qbClient = None;
        return;

    host = host + ":" + port;
    # print (json.dumps(host,indent=4));

    # instantiate a Client using the appropriate WebUI configuration
    # qbClient = qbittorrentapi.Client(host='localhost:****', username='***', password='***')
    try:
        qbClient = qbittorrentapi.Client(host=host, username=user, password=passwd, \
                # VERIFY_WEBUI_CERTIFICATE=False, SIMPLE_RESPONSES=True);
                VERIFY_WEBUI_CERTIFICATE=False );
    except qbittorrentapi.LoginFailed as e:
        print(e);

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
        # print (json.dumps(torrent,indent=4));
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

    # print (json.dumps(torrents,indent=4));

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
# TODO
def checkFileExistence():
    pass;


# 检查并确定torrentPath路径
def torrentPathCheck():

    global torrentPath;
    print ("I'm torrentPathCheck()...");

    # 优先使用E盘，如果没有E盘则使用D盘
    # 判断E/D盘的torrents文件夹是否存在,不存在就创建
    if os.path.exists('E:'):
        # print ("E:\\ exists, will using E:\\...");
        if os.path.exists('E:\\torrents'):
            print ("E:\\torrents\\ exists, will using E:\\torrents\\...");
            torrentPath = 'E:\\torrents\\';
        else:
            print ("E:\\torrents\\ not exists, Creating and using it ...");
            os.mkdir('E:\\torrents\\');
            torrentPath = 'E:\\torrents\\';
    elif os.path.exists('D:'):
        # print ("D:\ exists, will using D:\\...");
        torrentPath = 'D:\\';
        if os.path.exists('D:\\torrents'):
            print ("D:\\torrents\\ exists, will using D:\\torrents\\...");
            torrentPath = 'D:\\torrents\\';
        else:
            print ("D:\\torrents\\ not exists, Creating and using it ...");
            os.mkdir('D:\\torrents\\');
            torrentPath = 'D:\\torrents\\';
    else:
        print ("E: and D: are both not exist!!! Terminating ...");
        exit();

    print ("torrentPathCheck done...!\n");


# 按tracker来重命名种子文件
def renameTorrent(torrentPath, cate=None, type='first'):

    print ("I'm renameTorrent()...");
    print ("Renaming type is -> " + type);

    winerror = [];
    for file in os.listdir(torrentPath):
        if os.path.isfile( torrentPath + file) & file.endswith('.torrent'):
            print ( torrentPath + file);

            torrent_metadata = Bencode.read_file( torrentPath + file );
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
                        if os.path.join(torrentPath, file_new) == os.path.join(torrentPath, file):
                            print (file);
                            print ("No need to Rename...\n");
                            pass;
                        else:
                            print (file + " Renaming -> \n" + file_new );
                            os.rename(os.path.join(torrentPath, file),os.path.join(torrentPath, file_new));
                            print ("");
                    except WindowsError:
                        pass;
                        # winerror.append(file)

    print ("renameTorrent done...!\n");


# 复制qb暂停种子的torrent文件到特定目录
def copyPausedTorrentFile(qbClient, torrentPath, qb_path, cateDict=None):

    print ("I'm copyPausedTorrentFile()...");

    torrents = qbClient.torrents_info(filter='paused');
    # torrents = qbClient.torrents_info(category='');

    winerror = [];
    for torrent in torrents:
        # print(f'{torrent.hash}: {torrent.name[0:30]} ({torrent.state})')
        # print (torrent.hash + "|" + torrent.name[0:30] + "|" + torrent.save_path);

        print ("Copying " + torrent.hash + " to " + torrentPath + "...");
        torrent_file = qb_path + torrent.hash + ".torrent";
        # print (torrent_file);

        # 从qb BT_backup目录复制筛选出来的种子到torrentPath目录
        shutil.copy(torrent_file, torrentPath);

    print ("copyPausedTorrentFile done...!\n");


# 获取特定种子的信息
def getTorrentInfo(qbClient, cateDict=None):

    print ("I'm getTorrentInfo()...");

    # 筛选状态为"paused 暂停"的种子
    torrents = qbClient.torrents_info(filter='paused');
    # torrents = qbClient.torrents_info(filter='active');

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


# 对qb的限速进行自动设置
def autoSpeedLimit(qbClient, upSpeed):
    print ("I'm autoSpeedLimit()...");

    # 获取当前时间
    # print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    hour = int(time.strftime("%H", time.localtime()));
    if ( hour < 9 ) and ( hour > 0 ):
        print (hour, "点,晚上");
        isDaytime = 0;
    else:
        print (hour, "点,白天");
        isDaytime = 1;

    # 获取当前活动的种子列表
    torrents = qbClient.torrents_info(filter='active');
    # print (json.dumps(torrents, indent = 4));

    # 获取qb全局上传限速值
    global_transfer = qbClient.transfer.info;
    print (json.dumps(global_transfer, indent = 4));
    if ( global_transfer.up_rate_limit == 0 ) and ( isDaytime == 0 ):
        if ( global_transfer.up_info_speed/1024 < upSpeed ):
            # 0-9点之间,全局限速为0(即不限速)且全局上传速度小于配置文件中定义的值时
            print ("Night Time, Global UP limit: UNLIMITED && UP < " , upSpeed , "KB/s!!!");
            for torrent in torrents:
                # print (json.dumps(torrent, indent = 4));
                torrentProperties = qbClient.torrents_properties(torrent_hash = torrent.hash);
                if (torrent.up_limit != -1) and (torrent.up_limit != 0) :
                    # 对当前活动且有上传限速的种子解除限速
                    # print (f'{torrent.name[0:30]}|{torrent.up_limit/1024}kb/s|{torrent.category}');
                    print (f'{torrent.name[0:30]}' + " -> UP limit to None...");
                    torrent.set_upload_limit(limit=-1,torrent_hash=torrent.hash);
                else:
                    print (f'{torrent.name[0:30]}|{torrent.category}|',"UP speed UNLIMITED... Skipping...");
        else:
            # 0-9点之间,全局无限速且上传大于配置文件定义的值时不做任何操作
            print ("Night Time, Global UP limit: UNLIMITED && UP > " , upSpeed , "KB/s, skipping...");
            pass;
    elif ( global_transfer.up_rate_limit != 0 ) and ( isDaytime == 0 ):
        # 0-9点之间且全局限速时,解除限速
        print ("Night Time, Global UP limit: ", global_transfer.up_rate_limit/1024, " KB/s");
        print ("Setting global up limit to UNLIMITED...");
        qbClient.transfer_set_upload_limit( 0 );
    elif ( isDaytime == 1 ):
        # 0-9点之外,即白天时,不做任何操作
        print ("Day Time, Global UP limit: ", global_transfer.up_rate_limit/1024, " KB/s, skipping...");
        pass;

    print ("autoSpeedLimit done...!\n");


# 对http的tracker批量修改为https
def trackerHTTPS(qbClient, torrentCate=None):
    print ("I'm trackerHTTPS()...");

    print ("Input torrentCate is:" + torrentCate);

    torrents = qbClient.torrents_info(category=torrentCate);
    if len(torrents) == 0:
        print ("No torrent with given category!! Terminated!!\n");
        exit();

    # 依次对获取到的torrent进行替换tracker
    for torrent in torrents:
        for tracker in torrent.trackers:
            trackerUrl = tracker.url;
            if (trackerUrl.startswith('http://')):
                print ("\nNon HTTPS tracker found!!!...");
                print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')
                # print (trackerUrl);

                # 替换tracker的http为https且只替换一次
                trackerUrl_new = trackerUrl.replace("http://", "https://", 1);
                print (trackerUrl[0:30] + " --> " + trackerUrl_new[0:30]);

                torrent.edit_tracker(orig_url=trackerUrl, new_url=trackerUrl_new );
                # print (trackerUrl);
                # print (json.dumps(torrent,indent=4));
            elif (trackerUrl.startswith('https://')):
                print ("\nTorrent Already has HTTPS tracker...");
                # print (trackerUrl);
                pass;

    print ("trackerHTTPS done...!\n");


def main():
    print ("I'm main()...", "\n");

    global hostDict;
    global cateDict;
    global labelDict;
    global qbClient;
    global torrentPath;
    global torrents;
    global isLocal;

    # 接收输入选项前先读取qb_auto.ini配置文件
    readConf();
    # print (host,user,passwd);
    # print (json.dumps(cateDict,indent=4));
    # print (json.dumps(labelDict,indent=4));
    # print (json.dumps(hostDict,indent=4));

    print ("    * * * *  功 能 菜 单  * * * *    \n");
    print ("1. 将qb未分类种子按预定义规则进行分类。");
    print ("2. 重命名特定目录下的torrent种子文件。");
    print ("3. 将qb暂停的种子的torrent文件复制到特定目录并重命名。");
    print ("4. 获取qb特定种子的信息。");
    print ("5. 对qb中tracker为http的种子修改为https。");
    print ("请输入需要使用的功能选项：(直接回车默认选择1) \n");

    # 定义qb BT_backup路径
    qb_path = r'D:/_software/_internet/qbittorrent/profile/qBittorrent/data/BT_backup/';

    # 外部传入参数"1"时自动执行
    option = "0";
    try:
        if( sys.argv[1] == "1" ):
            option = "1";
            print ("按传入参数1开始执行... \n");
    except:
        # 无传入参数时等待用户输入，判断执行什么功能函数
        option = input("");
        # print (option);

    if option == "" or option == "1":
        # print ("输入为空");

        ### test - to - del
        # # # torrentPathCheck();
        # # # exit();
        ### test - to - del

        for conn in hostDict:
            # print (json.dumps(conn, indent=4));

            # 连接qb webapi
            qbConn(conn['host'], conn['port'], conn['user'], conn['password']);

            # 强制重新汇报所有种子
            # 当qbclient可连接时才执行
            if (qbClient):
                forceReannounce(qbClient);
                pass;
            # forceReannounce(qbClient,'frds');

            # 自动配置上传速度限制
            if (qbClient):
                autoSpeedLimit(qbClient, int(conn['upspeed']));

            # 自动对未分类种子进行分类
            # 当qbclient可连接时才执行
            if (qbClient):
                autoCate(qbClient, cateDict);
            # print ("Hahaha -> 直接回车或1");

    elif option == "2":
        print ("请输入需要重命名的种子的路径：(直接回车默认使用E:或D:/torrents/)");
        torrentPath = input("");
        if torrentPath == "":
            print ("输入path路径为空, 使用E:或D:/torrents/...");
            torrentPathCheck();
            pass;

        print ("请输入种子的pt站名位置: (直接回车默认为站名在前,其它任何字符为默认在后)");
        type = input("");
        if type == "":
            # print ("first");
            # print (torrentPath);
            renameTorrent(torrentPath);
        else:
            # print ("last");
            # print (torrentPath);
            renameTorrent(torrentPath, type='last');

    elif option == "3":
        for conn in hostDict:
            # print (conn);

            # 连接qb webapi
            qbConn(conn['host'], conn['port'], conn['user'], conn['password']);

            # 当qbclient可连接时才执行
            if (qbClient):
                # 当qb为本地运行且处于暂停的种子数量大于0时才执行
                if (isLocal == "1") and (len(qbClient.torrents_info(filter='paused'))):
                    print ("请输入需要重命名的种子的路径：(直接回车默认使用E:或D:/torrents/)");
                    torrentPath = input("");
                    if torrentPath == "":
                        print ("输入path路径为空, 使用E:或D:/torrents/...");
                        torrentPathCheck();
                        pass;

                    print ("请输入种子的pt站名位置: (直接回车默认为站名在前,其它任何字符为默认在后)");
                    type = input("");

                    # 拷贝暂停的种子文件
                    copyPausedTorrentFile(qbClient, torrentPath, qb_path);

                    if type == "":
                        print ("first");
                        renameTorrent(torrentPath);
                    else:
                        print ("last");
                        renameTorrent(torrentPath, type='last');
                else:
                    print ("qb is not running localhost or No paused torrent... Will not copy paused torrents...\n");

    elif option == "4":
        for conn in hostDict:
            # print (conn);

            # 连接qb webapi
            qbConn(conn['host'], conn['port'], conn['user'], conn['password']);

            # 当qbclient可连接时才执行
            if (qbClient):
                getTorrentInfo(qbClient, cateDict=None);

    elif option == "5":

        # print (json.dumps(cateDict, indent=4));
        # print (cateDict.values());

        print ("请输入需要修改为https tracker的种子分类名称：(直接回车将对所有种子进行tracker检查)");
        torrentCate = input("");
        if torrentCate == "":
            print ("输入种子分类为空, 将对所有种子进行tracker检查...");
            pass;
        elif torrentCate in cateDict.values():
            print ("输入站点分类名为已在配置文件中定义的站点：" + torrentCate);
        else:
            print ("输入站点分类未在配置文件中定义，Terminated!!!....\n");
            exit();

        for conn in hostDict:
            # print (conn);

            # 连接qb webapi
            qbConn(conn['host'], conn['port'], conn['user'], conn['password']);

            # 当qbclient可连接时才执行
            if (qbClient):
                trackerHTTPS(qbClient, torrentCate);



    # autoLabel(qbClient, labelDict);


if __name__ == '__main__':
    main();
