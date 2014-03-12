import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os
import json

class DuplicatePlayerException(Exception):
    pass

class PlayerNotFoundException(Exception):
    pass

class DuplicateGameException(Exception):
    pass

class GameNotFoundException(Exception):
    pass

class Player():
    def __init__(self, player_id):
        self.player_id = player_id
        self.connected = False
        self.has_pos = False
        self.lat = 0.0
        self.lon = 0.0

    def update_location(self, lat, lon):
        self.has_pos = True;
        self.lat = lat;
        self.lon = lon;

class Game():
    def __init__(self, game_id):
        self.game_id = game_id
        self.connections = set()
        self.players = {}

    def send_messages(self, message):
        for conn in self.connections:
            try:
                conn.write_message(message)
            except:
                print "error sending message"

    def __del__(self):
        # close all connections
        self.send_messages("game over")
        for conn in self.connections:
            try:
                conn.close()
            except:
                pass

    def add_player(self, player_id):
        if player_id in self.players:
            raise DuplicatePlayerException((self.game_id, player_id))
        self.players[player_id] = Player

    def get_player(self, player_id):
        if player_id not in self.players:
            raise PlayerNotFoundException((self.game_id, player_id))
        return self.players[player_id]

    def remove_player(self, player_id):
        if player_id not in self.players:
            raise PlayerNotFoundException((self.game_id, player_id)) 
        del self.players[player_id]

    def update_location(self, player_id, lat, lon):
        player = self.get_player(player_id)
        player.update_location(lat, lon)

games = {'test1':Game('test1'), 'test2':Game('test2')}

def create_game(game_id):
    if game_id in games:
        raise DuplicateGameException(game_id)
    games[game_id] = Game(game_id)

def remove_game(game_id):
    if game_id not in games:
        raise GameNotFoundException(game_id)
    del games[game_id]

def get_game(game_id):
    if game_id not in games:
        raise GameNotFoundException(game_id)
    return games[game_id]

class HTMLHandler(tornado.web.RequestHandler):
    def get(self, filename):
        self.render(filename)

class GameSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, game_id):
        self.game = get_game(game_id)
        self.game.connections.add(self)

    def on_message(self, message):
        self.game.send_messages(message)

    def on_close(self):
        self.game.connections.remove(self)

class GameLister(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps({"games":games.keys()}))


application = tornado.web.Application([
    (r'^/websockets/(.*)', GameSocketHandler),
    (r'^/api/games', GameLister),
    (r'^/(.*\.html)$', HTMLHandler),
    (r'^/(.*)$', tornado.web.StaticFileHandler, {"path": "."})
], debug=True)

if __name__ == '__main__':
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
