import asyncio
import websockets
from multiprocessing import Barrier, Condition, Process, Lock
import requests
from random import randint, choice
from time import time
from collections import defaultdict
import json
from sys import argv

num_threads = 10
num_loc_updates = 100

host = "localhost"

if len(argv) > 1:
	host = argv[1]

host_name = host + ":8888"
start_barrier = Barrier(num_threads)
end_barrier = Barrier(num_threads)



class WSRunner(Process):
	def __init__(self, url, d):
		Process.__init__(self)
		self.url = url
		self.d = d
		self.lock = Lock()
		self.lock.acquire()
	@asyncio.coroutine
	def ws(self):
		self.websocket = yield from websockets.connect(self.url)
		update_count = 0
		self.lock.release()
		while update_count < num_loc_updates * num_threads:
			update = yield from self.websocket.recv()
			update_count += 1
		# 	# j = json.loads(update)
		# 	# lat = float(j['lat'])
		# 	# lng = float(j['lng'])
		# 	# player_id = j['player_id']
		# 	# self.d[player_id] = (lat, lng)
		print("finished receiving")
		self.websocket.close()

	def run(self):
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)		
		loop.run_until_complete(self.ws())

class TestClient(Process):
	def __init__(self, map_id):
		Process.__init__(self)
		self.map_id = map_id
		self.locations = defaultdict(lambda : (0,0))
		self.host_name = host_name

	def run(self):
		# create a new player
		new_player_data = {'player_name' : 'tyrone'}
		new_player_url = 'http://%s/maps/%s/create_player' % (self.host_name, self.map_id)
		r = requests.post(new_player_url, data = new_player_data)
		j = r.json()
		self.player_id = int(j['player_id'])
		# connect to the socket
		websocket_url = 'ws://%s/maps/%s/channel' % (self.host_name, self.map_id)
		self.client = WSRunner(websocket_url, self.locations)
		self.client.start()
		self.client.lock.acquire()
		# inform the start barrier
		start_barrier.wait()
		# fire random updates
		for i in range(num_loc_updates):
			lat = randint(1, 90)
			lng = randint(1, 90)
			player_update_url = 'http://%s/maps/%s/update_player' % (self.host_name, self.map_id)
			update_data = {'player_id' : self.player_id, 'lat' : lat, 'lng' : lng}
			r = requests.post(player_update_url, data = update_data)
		print("finished updates")
		self.client.join()
		# inform the end barrier
		end_barrier.wait()
		# delete self
		delete_player_data = {'player_id' : self.player_id}
		delete_player_url = 'http://%s/maps/%s/delete_player' % (self.host_name, self.map_id)
		r = requests.post(delete_player_url, data = delete_player_data)


if __name__ == '__main__':
	start_time = time()
	# create a map
	new_map_data = {'map_name' : 'stress tester'}
	new_map_url = 'http://%s/maps/create_map' % (host_name)
	r = requests.post(new_map_url, data = new_map_data)
	j = r.json()
	map_id = j['map_id']
	threads = [TestClient(map_id) for i in range(num_threads)]
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	maps = requests.get('http://%s/maps' % (host_name)).json()
	for m in maps:
		map_name = m['map_name']
		if map_name == 'stress tester':
			map_id = m['map_id']
			kill_map_data = {'map_id' : map_id}
			kill_map_url = 'http://%s/maps/delete_map' % (host_name)
			r = requests.post(kill_map_url, data = kill_map_data)
	end_time = time()
	print("total", end_time - start_time)