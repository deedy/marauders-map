import tornado.httpserver
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.gen
import json
import datetime
import time

import tornadoredis
from tornadoredis.pubsub import BaseSubscriber

import database

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"

class MultiSub(BaseSubscriber):
    def on_message(self, msg):
        if not msg:
            return
        if msg.kind == 'message' and msg.body:
            # Get the list of subscribers for this channel
            subscribers = list(self.subscribers[msg.channel].keys())
            for sub in subscribers:
                sub.pubsub_message(msg)

c = tornadoredis.Client()
c.connect()
sub_handler = MultiSub(c)

d = tornadoredis.Client()
d.connect()

class MapLister(tornado.web.RequestHandler):
    def get(self):
        map_infos = database.get_map_infos()
        to_send = json.dumps(map_infos)
        self.write(to_send)

class PlayerListerAll(tornado.web.RequestHandler):
    def get(self):
        player_infos = database.get_player_infos()
        to_send = json.dumps(player_infos)
        self.write(to_send)

class MapListerAll(tornado.web.RequestHandler):
    def get(self):
        map_infos = database.get_map_infos()
        to_send = json.dumps(map_infos)
        self.write(to_send)

class MapListerForPlayer(tornado.web.RequestHandler):
    def get(self, player_id):
        map_infos = database.get_map_infos()
        map_infos_player = database.get_map_infos_for_player(player_id)
        maps_id_player = [m["map_id"] for m in map_infos_player]
        map_wo_player = [m for m in map_infos if not m["map_id"] in maps_id_player]
        maps = {
            "resume": map_infos_player,
            "join": map_wo_player
         }
        self.write(json.dumps(maps))

class PlayerListerForMap(tornado.web.RequestHandler):
    def get(self, map_id):
        player_infos = database.get_player_infos_for_map(map_id)
        to_send = json.dumps(player_infos)
        self.write(to_send)

class MapCreator(tornado.web.RequestHandler):
    def post(self):
        map_name = self.get_argument("map_name")
        new_map_id = database.create_new_map(map_name)
        map_dict = database.get_map_info(new_map_id)
        to_send = json.dumps(map_dict)
        self.write(to_send)

class PlayerCreatorAndAdd(tornado.web.RequestHandler):
    def post(self, map_id):
        player_name = self.get_argument("player_name")
        new_player_id = database.create_new_player(player_name)
        database.add_player_to_map(map_id, new_player_id)
        player_info = database.get_player_info(new_player_id)
        to_send = json.dumps(player_info)
        self.write(to_send)

class MapDeleter(tornado.web.RequestHandler):
    def post(self):
        map_id = self.get_argument("map_id")
        database.delete_map(map_id)

class PlayerDeleter(tornado.web.RequestHandler):
    def post(self, map_id):
        player_id = self.get_argument("player_id")
        database.delete_player(player_id)


class LocationUpdater(tornado.web.RequestHandler):
    def post(self):
        player_id = self.get_argument("player_id")
        lat = float(self.get_argument("lat"))
        lng = float(self.get_argument("lng"))
        database.update_location(player_id, lat, lng)
        player_tail = database.get_player_locations(player_id, sys.maxint)
        message = {
            "player_id" : player_id,
            "player_tail" : player_tail,
            "last_updated_string" : pretty_date(int(player_tail[0]['created']/1000))
        }
        publish_location_update(player_id, message)

def publish_location_update(player_id, player_info):
    map_ids = database.get_map_ids_for_player(player_id)
    print map_ids
    for map_id in map_ids:
        channel_name = "maps:%s:location_updates" % map_id
        to_send = json.dumps(player_info)
        print to_send
        d.publish(channel_name, to_send)

class MessageHandler(tornado.websocket.WebSocketHandler):
    def open(self, map_id):
        self.map_id = map_id
        sub_handler.subscribe('maps:%s:location_updates' % self.map_id, self)
        # self.listen()

    # @tornado.gen.engine
    # def listen(self):
    #     self.client = tornadoredis.Client()
    #     self.client.connect()
    #     yield tornado.gen.Task(self.client.subscribe, 'maps:%s:location_updates' % self.map_id)
    #     self.client.listen(self.pubsub_message)

    def pubsub_message(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))
        if msg.kind == 'disconnect':
            self.close()

    def on_message(self, msg):
        pass

    def on_close(self):
        # if self.client.subscribed:
        #     self.client.unsubscribe('maps:%s:location_updates' % self.map_id)
        #     self.client.disconnect()
        sub_handler.unsubscribe('maps:%s:location_updates' % self.map_id, self)

class HTMLHandler(tornado.web.RequestHandler):
    def get(self, filename):
        self.render(filename)

class SignInForm(tornado.web.RequestHandler):
    def post(self):
        map_id = str(self.get_argument("map_id"))
        player_id = str(self.get_argument("player_id"))
        player_status = str(self.get_argument("player"))
        map_status = str(self.get_argument("entry"))
        print player_status
        if player_status == "new":
            player_id = database.create_new_player(str(self.get_argument("player_name")))
            database.create_random_path(player_id)
        if map_status == "join":
            database.add_player_to_map(map_id, player_id)
        self.redirect("/maps/"+str(map_id)+"?player_id="+str(player_id))


class GetGame(tornado.web.RequestHandler):
    def get(self, map_id):
        player_id = self.get_argument("player_id")
        print player_id+"\n\n\n"
        all_maps = database.get_map_infos()
        map_details = database.get_map_info(map_id)
        tornadovars = {}
        tornadovars['map_id'] = map_id
        tornadovars['map_name'] = map_details['map_name']
        tornadovars['map_created'] = datetime.datetime.fromtimestamp(int(map_details['created']/1000)).strftime('%Y-%m-%d %H:%M:%S')
        tornadovars['center_lat'] = map_details['lat']
        tornadovars['center_lng'] = map_details['lng']

        player_details = database.get_player_infos_for_map(map_id)
        player_locations = database.get_players_locations_for_map(map_id,sys.maxint)
        player_info = {}
        for i in player_details:
            if not str(i['player_id']) in player_info:
                player_info[str(i['player_id'])] = {}
            player_info[str(i['player_id'])]['info'] = i
            player_info[str(i['player_id'])]['id'] = str(i['player_id'])
        for i in player_locations:
            if not i[0] in player_info:
                player_info[i[0]] = {}
            player_info[i[0]]['locations'] = i[1]
            player_info[i[0]]['last_updated_string'] = pretty_date(int(i[1][0]['created']/1000))
        print player_info
        self.render("index3.html", tornadovars=tornadovars, player_details=player_info, all_maps = all_maps, player_id = player_id)

    def post(self, map_id):
        player_id = self.get_argument("player_id")
        print player_id+"\n\n\n"
        all_maps = database.get_map_infos()
        map_details = database.get_map_info(map_id)
        tornadovars = {}
        tornadovars['map_id'] = map_id
        tornadovars['map_name'] = map_details['map_name']
        tornadovars['map_created'] = datetime.datetime.fromtimestamp(int(map_details['created']/1000)).strftime('%Y-%m-%d %H:%M:%S')
        tornadovars['center_lat'] = map_details['lat']
        tornadovars['center_lng'] = map_details['lng']
        player_details = database.get_player_infos_for_map(map_id)
        player_locations = database.get_players_locations_for_map(map_id,sys.maxint)
        player_info = {}
        for i in player_details:
            if not str(i['player_id']) in player_info:
                player_info[str(i['player_id'])] = {}
            player_info[str(i['player_id'])]['info'] = i
            player_info[str(i['player_id'])]['id'] = str(i['player_id'])
        for i in player_locations:
            if not i[0] in player_info:
                player_info[i[0]] = {}
            player_info[i[0]]['locations'] = i[1]
            player_info[i[0]]['last_updated_string'] = pretty_date(int(i[1][0]['created']/1000))
        print player_info
        self.render("index3.html", tornadovars=tornadovars, player_details=player_info, all_maps = all_maps, player_id = player_id)

class DefaultHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class ResetListener(tornado.web.RequestHandler):
    def post(self):
        database.test_script()
        map_ids = database.get_map_ids()
        for map_id in map_ids:
            channel_name = "maps:%s:location_updates" % map_id
            to_send = json.dumps({"CLEAR":[]});
            d.publish(channel_name, to_send)

class SimulateLister(tornado.web.RequestHandler):
    def post(self):
        player_id = int(self.get_argument("player_id"))
        for point in database.loop:
            print point
            lat = float(point[0])
            lng = float(point[1])
            database.update_location(player_id, lat, lng)
            player_tail = database.get_player_locations(player_id, sys.maxint)
            message = {
                "player_id" : player_id,
                "player_tail" : player_tail,
                "last_updated_string" : pretty_date(int(player_tail[0]['created']/1000))
            }
            publish_location_update(player_id, message)

application = tornado.web.Application([
    (r'/flush', ResetListener),
    (r'/simulate', SimulateLister),
    (r'/maps', MapLister),
    (r'/maps/create_map', MapCreator),
    (r'/maps/delete_map', MapDeleter),
    (r'/maps/all_players', PlayerListerAll),
    (r'/maps/all_maps', MapListerAll),
    (r'/signin', SignInForm),
    (r'/maps/(.*)/map_players', MapListerForPlayer),
    (r'/maps/(.*)/players_map', PlayerListerForMap),
    (r'/maps/(.*)/create_player', PlayerCreatorAndAdd),
    (r'/maps/(.*)/delete_player', PlayerDeleter),
    (r'/update_player', LocationUpdater),
    (r'/maps/(.*)/channel', MessageHandler),
    (r'/maps/(.*)', GetGame),
    (r'/', DefaultHandler),
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
    print('Demo is runing at 0.0.0.0:8888\nQuit the demo with CONTROL-C')
    tornado.ioloop.IOLoop.instance().start()
