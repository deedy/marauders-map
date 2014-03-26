import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import json

import tornadoredis
import redis

c = tornadoredis.Client()
c.connect()
r = redis.Redis()

class MapLister(tornado.web.RequestHandler):
	def get(self):
		map_ids = r.smembers("map_ids")
		# get all the map names
		map_names = r.mget(["maps:%s" for s in map_ids], [])
		# make a dict
		zipped = zip(map_ids, map_names)
		map_json = [{"map_id" : mid, "map_name" : mname} for (mid, mname) in zipped]
		# ship it
		self.write(json.dumps(map_json))

class MapCreator(tornado.web.RequestHandler):
	def post(self):
		# get the map name argument
		try:
			map_name = self.get_argument("map_name")
		except:
			self.clear()
			self.set_status(400)
			self.finish("<html><body>Need the 'map_name' argument</body></html>")
			return
		# get a map id
		map_id = r.incr("map_id_counter")
		# create a new map key with this id
		map_key = "map:%s" % map_id
		# store the map name as the value
		r.set(map_key, map_name)
		# add the map id to the set of map ids
		r.sadd("map_ids", map_id)


class MapDeletor(tornado.web.RequestHandler):
	def post(self):
		try:
			map_id = self.get_argument("map_id")
		except:
			self.clear()
			self.set_status(400)
			self.finish("<html><body>Need the 'map_id' argument</body></html>")
			return
		map_key = "map:%s" % map_id
		plist_key = map_key + ":players"
		# delete the map
		r.delete(map_key)
		# delete the set of players
		r.delete(plist_key)

class PlayerLister(tornado.web.RequestHandler):
	def get(self, map_id):
		# create the player set key
		plist_key = "map:%s:players" % map_id
		# get the set of player ids
		players = r.smembers(plist_key)
		# get the hashes all at once
		fields = ['name', 'lat', 'lng']
		pipe = r.pipeline()
		for player_id in players:
			player_key = plist_key + (":%s" % player_id)
			pipe.hmget(player_key, fields)
		player_hashes = pipe.execute()
		# don't list players without a location
		player_json = [dict(zip(fields, pl)) for pl in player_hashes if pl[1] and pl[2]]
		# ship it
		self.write(json.dumps(player_json))

class PlayerCreator(tornado.web.RequestHandler):
	def post(self, map_id):
		# make the map key
		map_key = "map:%s" % map_id
		# get the player name argument
		player_name = self.get_argument("player_name")
		# get a new player id
		player_id = r.incr(map_key + ":player_id_counter")
		# create a player key
		player_key = map_key + ":players:%s" % player_id
		# create the player
		r.hset(player_key, "name", player_name)
		# add player to set of players
		r.sadd(map_key + ":players", player_id)



application = tornado.web.Application([
	(r'/maps', MapLister),
	(r'/maps/create_map', MapCreator),
	(r'/maps/delete_map', MapDeletor),
	(r'/maps/(.*)/players', PlayerLister),
	(r'/maps/(.*)/create_player', PlayerCreator)
])

if __name__ == '__main__':
	# clean the DB
	# r.flushall()
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(8888)
	print('Demo is runing at 0.0.0.0:8888\nQuit the demo with CONTROL-C')
	tornado.ioloop.IOLoop.instance().start()