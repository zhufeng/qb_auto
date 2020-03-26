import qbittorrentapi
import re

f= open("qb_auto_ext.txt","r");
lines = f.read().splitlines();
# print (lines);
# host = lines[0];
host = lines[3];
user = lines[1];
passwd = lines[2];
# print (lines);
# print ({user});
print ({host});
f.close();

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
for k,v in qbt_client.app.build_info.items():
    print(f'{k}: {v}');

# retrieve and show all torrents
# for torrent in qbt_client.torrents_info():
    # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

# pause all torrents 
# # # # # qbt_client.torrents.pause.all()

# print (qbt_client.torrents_info(status_filter='active'));

# for torrent in qbt_client.torrents_info():
    # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

# torrents = qbt_client.torrents_info(category='');

for torrent in qbt_client.torrents_info(category=''):
# for torrent in qbt_client.torrents_info():
    # print(f'{torrent.hash[10:]}: {torrent.name} - {torrent.state}');
    # print (torrent.tracker[0:30], torrent.name[0:15]);
    tracker = torrent.tracker;
    # print (tracker[0:30]);
    if re.search(r'league',tracker):
        torrent.set_category(category='leaguehd');
        print ("Categorized!!!!");
    else:
        print ("NOT MATCH");

    # if tracker



# print (torrents);

