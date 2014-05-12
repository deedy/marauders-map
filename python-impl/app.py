import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import json
ioloop = tornado.ioloop.IOLoop.instance()

# from multiprocessing import Process, Queue, Lock, Condition
from threading import Thread
from Queue import Queue
import tornadoredis
from tornadoredis.pubsub import BaseSubscriber

import database

# class WaitFreeQueue:
# 	def __init__(self):
# 		self.q = Queue()
# 		self.lock = Lock
# 		self.has_items = Condition(self.lock)

# 	def get(self):
# 		with self.lock:
# 			while self.q.empty():
# 				self.has_items.wait()


# class MultiSub(BaseSubscriber):
#     def on_message(self, msg):
#         if not msg:
#             return
#         if msg.kind == 'message' and msg.body:
#             # Get the list of subscribers for this channel
#             subscribers = list(self.subscribers[msg.channel].keys())
#             pub_q.put((msg, subscribers))

# c = tornadoredis.Client()
# c.connect()
# sub_handler = MultiSub(c)

redis_host = 'localhost'
d = tornadoredis.Client(host=redis_host)
d.connect()

def publish_location_update(map_id, player_info):
	channel_name = "maps:%s:location_updates" % map_id
	to_send = json.dumps(player_info)
	d.publish(channel_name, to_send)

class MapLister(tornado.web.RequestHandler):
	def get(self):
		map_infos = database.get_map_infos()
		to_send = json.dumps(map_infos)
		self.write(to_send)

class MapCreator(tornado.web.RequestHandler):
	def post(self):
		map_name = self.get_argument("map_name")
		new_map_id = database.create_new_map(map_name)
		map_dict = database.get_map_info(new_map_id)
		to_send = json.dumps(map_dict)
		self.write(to_send)

class MapDeleter(tornado.web.RequestHandler):
	def post(self):
		map_id = self.get_argument("map_id")
		database.delete_map(map_id)

class PlayerLister(tornado.web.RequestHandler):
	def get(self, map_id):
		player_infos = database.get_player_infos(map_id)
		to_send = json.dumps(player_infos)
		self.write(to_send)

class PlayerCreator(tornado.web.RequestHandler):
	def post(self, map_id):
		player_name = self.get_argument("player_name")
		new_player_id = database.create_new_player(map_id, player_name)
		player_info = database.get_player_info(map_id, new_player_id)
		to_send = json.dumps(player_info)
		self.write(to_send)

class PlayerDeleter(tornado.web.RequestHandler):
	def post(self, map_id):
		player_id = self.get_argument("player_id")
		database.delete_player(map_id, player_id)


class LocationUpdater(tornado.web.RequestHandler):
	def post(self, map_id):
		player_id = self.get_argument("player_id")
		lat = self.get_argument("lat")
		lng = self.get_argument("lng")
		# if database.player_id_exists(map_id, player_id):
		# 	database.update_location(map_id, player_id, lat, lng)
		message = {
			"player_id" : player_id,
			"lat" : lat,
			"lng" : lng
		}
		publish_location_update(map_id, message)
		print message

class MessageHandler(tornado.websocket.WebSocketHandler):
	def open(self, map_id):
		print "new socket connection"
		self.map_id = map_id
		self.channel_name = 'maps:%s:location_updates' % self.map_id
		# sub_handler.subscribe(self.channel_name, self)
		self.client = tornadoredis.Client()
		self.client.connect()
		self.listen()

	@tornado.gen.engine
	def listen(self):
		self.client = tornadoredis.Client()
		self.client.connect()
		yield tornado.gen.Task(self.client.subscribe, self.channel_name)
		self.client.listen(self.pubsub_message)

	def pubsub_message(self, msg):
		if msg.kind == 'message':
			self.write_message(str(msg.body))
			print "writing to socket"
		if msg.kind == 'disconnect':
			self.close()

	def on_message(self, msg):
		pass

	def on_close(self):
		# sub_handler.unsubscribe(self.channel_name, self)
		print "socket closing"
		if self.client.subscribed:
			self.client.unsubscribe(self.channel_name)
			self.client.disconnect()

class HTMLHandler(tornado.web.RequestHandler):
	def get(self, filename):
		self.render(filename)

application = tornado.web.Application([
	(r'/maps', MapLister),
	(r'/maps/create_map', MapCreator),
	(r'/maps/delete_map', MapDeleter),
	(r'/maps/(.*)/players', PlayerLister),
	(r'/maps/(.*)/create_player', PlayerCreator),
	(r'/maps/(.*)/delete_player', PlayerDeleter),
	(r'/maps/(.*)/update_player', LocationUpdater),
	(r'/maps/(.*)/channel', MessageHandler),
	(r'^/(.*\.html)$', HTMLHandler),
	(r'^/(.*)$', tornado.web.StaticFileHandler, {"path": "."})
], debug=True)

if __name__ == '__main__':
	http_server = tornado.httpserver.HTTPServer(application)
	import sys
	port = 8888
	if len(sys.argv) > 1:
		port = int(sys.argv[1])
	http_server.listen(port)
	print('Demo is runing at 0.0.0.0:%d\nQuit the demo with CONTROL-C' % port)
	ioloop.start()