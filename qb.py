import os
import re
import bencode
import telnetlib
import configparser
import qbittorrentapi

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

    print ("Using: " + user + "@" + host + ":" + port + "....");

    # 读取配置文件中[category]分类部分
    cateDict = cfg._sections['category'];
    # print (cateDict);

    # 读取配置文件中[label]标签部分
    labelDict = cfg._sections['label'];
    # print (labelDict);

    print ("");


# 连接到qb webui
def qbConn(host,port,user,passwd):
    print ("I'm qbConn()...");

    global qbClient;
    host = host + ":" + port;
    print (host);

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

    print ("");


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


# 对种子的文件内容进行简单地文件存在检查
def checkFileExistence():
    pass;


# 按tracker来重命名种子文件
def renameTorrent(path, cate=None, type='first'):
    
    print ("Renaming type is -> " + type);

    winerror = []
    for root, dirlist, filelist in os.walk(path):
        for file in filelist:
            # file = path + file;
            # print (file);

            with open((path+file), 'rb') as fh:
                torrent_file = fh.read();

            torrent_metadata = bencode.decode(torrent_file);
            torrent_tracker = torrent_metadata[b'announce'][0:50];
            torrent_name = torrent_metadata[b'info'][b'name'].decode('utf8');
            # print (torrent_tracker);
            # print (torrent_name + '\n');
            # exit();

            for k,v in cateDict.items():
                # print (k);
                if re.search(k, torrent_tracker.decode()):
                    # print (v)
                    file_site_first = '[' + v + ']_' + torrent_name + '.torrent';
                    file_site_last = torrent_name + '_[' + v + ']' + '.torrent';

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
                            # print('Now Renaming:', file, 'To', file_new)
                            print (file + " -> \n" + file_new );
                            os.rename(os.path.join(path, file),os.path.join(path, file_new));
                            print ("");
                    except WindowsError:
                        pass;
                        # winerror.append(file)


def main():
    print ("I'm main()...", "\n");

    global host;
    global port;
    global user;
    global passwd;
    global cateDict;
    global labelDict;
    global qbClient;

    readConf();
    # print (host,user,passwd);
    # print (cateDict);
    # print (labelDict);
    qbConn(host, port, user, passwd);

    forceReannounce(qbClient);
    # forceReannounce(qbClient,'frds');

    autoCate(qbClient, cateDict);

    # autoLabel(qbClient, labelDict);

    path = r'E:\torrents\\';
    # renameTorrent(path);
    # renameTorrent(path, type='last');


if __name__ == '__main__':
    main();


