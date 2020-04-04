import os
import re
import configparser
import qbittorrentapi


def readConf():
    print ("I'm readConf()...");

    global host;
    global user;
    global passwd;
    global cateDict;
    global labelDict;

    cfg = configparser.ConfigParser();
    if os.path.exists('qb_auto1.ini'):
        cfg.read_file(open("qb_auto1.ini"));
        print ("Reading qb_auto1.ini...");
    else:
        cfg.read_file(open("qb_auto.ini"));
        print ("Reading qb_auto.ini...");
    # print (cfg.sections());

    # 读取配置文件中qb webui[connection]登录信息部分
    host = cfg['connection']['localhost'];
    # host = cfg['connection']['host']);
    user = cfg['connection']['user'];
    passwd = cfg['connection']['password'];

    # 读取配置文件中[category]分类部分
    cateDict = cfg._sections['category'];
    # print (cateDict);

    # 读取配置文件中[label]标签部分
    labelDict = cfg._sections['label'];
    # print (labelDict);

    print ("");


def qbConn(host,user,passwd):
    print ("I'm qbConn()...");

    global qbClient;

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


def autoCate(qbClient):
    print ("I'm autoCate()...");

    # for torrent in qbClient.torrents_info():
    for torrent in qbClient.torrents_info(category=''):
        # for torrent in qbtCon.torrents_info(category='frds'):
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

    print ("AutoCate done...!", "\n");


def autoLabel(qbClient):
    pass;


def forceReport():
    pass;


def main():
    print ("I'm main()...", "\n");

    global host;
    global user;
    global passwd;
    global cateDict;
    global labelDict;
    global qbClient;

    readConf();
    # print (host,user,passwd,cateDict,labelDict);
    qbConn(host, user, passwd);
    autoCate(qbClient);


if __name__ == '__main__':
    main();


