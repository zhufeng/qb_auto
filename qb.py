import qbittorrentapi
import re

## 读取qb_auto_ext.txt文件中定义的qb webui的登录信息
userFile = open("qb_auto_ext.txt" , "r");
userLines = userFile.read().splitlines();
# print (userLines);
# host = userLines[3];
host = userLines[0];
user = userLines[1];
passwd = userLines[2];
# print (userLines);
print ({host});
print ({user});
userFile.close();


## 读取qb_categories.txt文件中定义的
## tracker名和分类名的对应关系，并生成字典
cateFile = open("qb_categories.txt" , "r");
# cateLines = cateFile.read().splitlines();
# print (cateLines);
cateDict = {};

while True:
    line = cateFile.readline().split("\n")[0];
    # print (line);
    if line == '':
        break
    index = line.find(':');
    # print (index);
    key = line[:index];
    value = line[index+1:];
    cateDict[key] = value;

cateFile.close();
# print (cateDict.items());
# for k,v in cateDict.items():
    # print (k, "=", v);


# instantiate a Client using the appropriate WebUI configuration
# qbt_client = qbittorrentapi.Client(host='localhost:****', username='***', password='***')
qbt_client = qbittorrentapi.Client(host=host, username=user, password=passwd);

# the Client will automatically acquire/maintain a logged in state in line with any request.
# therefore, this is not necessary; however, you many want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e);

# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}');
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}');
# for k,v in qbt_client.app.build_info.items():
    # print(f'{k}: {v}');

# retrieve and show all torrents
# for torrent in qbt_client.torrents_info():
    # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

# pause all torrents 
# # # # # qbt_client.torrents.pause.all()

# print (qbt_client.torrents_info(status_filter='active'));

# for torrent in qbt_client.torrents_info():
for torrent in qbt_client.torrents_info(category=''):
# for torrent in qbt_client.torrents_info(category='frds'):
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






