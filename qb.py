import qbittorrentapi
import re

# instantiate a Client using the appropriate WebUI configuration
qbt_client = qbittorrentapi.Client(host='localhost:****', username='***', password='***')

# the Client will automatically acquire/maintain a logged in state in line with any request.
# therefore, this is not necessary; however, you many want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# display qBittorrent info
print(f'qBittorrent: {qbt_client.app.version}')
print(f'qBittorrent Web API: {qbt_client.app.web_api_version}')
for k,v in qbt_client.app.build_info.items(): 
    print(f'{k}: {v}')

# retrieve and show all torrents
# for torrent in qbt_client.torrents_info():
    # print(f'{torrent.hash[-6:]}: {torrent.name} ({torrent.state})')

# pause all torrents
# # # # # qbt_client.torrents.pause.all()


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

