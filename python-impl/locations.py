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

def game_over_message(game_id):
    return json.dumps({
        "game_id" : game_id,
        "type" : "game_over"
    })

def duplicate_game_message(game_id):
    return json.dumps({
        "game_id" : game_id,
        "type" : "duplicate_game"
    })

def game_not_found_message(game_id):
    return json.dumps({
        "game_id" : game_id,
        "type" : "game_not_found"
    })

def duplicate_player_message(game_id, player_id):
    return json.dumps({
        "game_id" : game_id,
        "player_id" : player_id,
        "type" : "duplicate_player"
    })

def player_not_found_message(game_id, player_id):
    return json.dumps({
        "game_id" : game_id,
        "player_id" : player_id,
        "type" : "player_not_found"
    })

def location_update_message(game_id, player_id, lat, lng):
    return json.dumps({
        "type" : "location_update",
        "game_id" : game_id,
        "player_id" : player_id,
        "lat" : lat,
        "lng" : lng
    })

class Player():
    def __init__(self, player_id):
        self.player_id = player_id
        self.connected = False
        self.has_pos = False
        self.lat = 0.0
        self.lng = 0.0

    def update_location(self, lat, lng):
        self.has_pos = True;
        self.lat = lat;
        self.lng = lng;

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
        self.send_messages(game_over_message(self.game_id))
        for conn in self.connections:
            try:
                conn.close()
            except:
                print "error closing connection"

    def add_player(self, player_id):
        if player_id in self.players:
            raise DuplicatePlayerException((self.game_id, player_id))
        self.players[player_id] = Player(player_id)

    def get_player(self, player_id):
        if player_id not in self.players:
            raise PlayerNotFoundException((self.game_id, player_id))
        return self.players[player_id]

    def remove_player(self, player_id):
        if player_id not in self.players:
            raise PlayerNotFoundException((self.game_id, player_id)) 
        del self.players[player_id]

    def update_location(self, player_id, lat, lng):
        player = self.get_player(player_id)
        player.update_location(lat, lng)
        self.send_messages(
            location_update_message(
                self.game_id,
                player_id,
                lat,
                lng
            )
        )

    def list_players(self):
        return [{
            "player_id" : pid,
            "lat" : player.lat,
            "lng" : player.lng
        } for (pid, player) in self.players.iteritems()]

games = {'test1':Game('test1'), 'test2':Game('test2')}
games['test1'].add_player('player1')
games['test1'].add_player('player2')

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
        try:
            self.game = get_game(game_id)
            self.game.connections.add(self)
            print "socket opened"
        except GameNotFoundException as e:
            print e
            game_id = e.message
            self.write_message(game_not_found_message(game_id))
            self.close()

    def on_message(self, message):
        try:
            print message
            data = json.loads(message)
            player_id = data["player_id"]
            lat = data["lat"]
            lng = data["lng"]
            self.game.update_location(
                player_id,
                lat,
                lng
            )
            print "location updated"
        except Exception as e:
            print e

    def on_close(self):
        try:
            self.game.connections.remove(self)
        except Exception as e:
            print e

class GameLister(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps({"games":games.keys()}))
        print "games listed"

class PlayerLister(tornado.web.RequestHandler):
    def get(self, game_id):
        game = get_game(game_id)
        msg = json.dumps({"players" : game.list_players()})
        self.write(msg);
        print "players listed"

application = tornado.web.Application([
    (r'^/api/games/(.*)/websocket', GameSocketHandler),
    (r'^/api/games/(.*)/list_players', PlayerLister),
    (r'^/api/list_games$', GameLister),
    (r'^/(.*\.html)$', HTMLHandler),
    (r'^/(.*)$', tornado.web.StaticFileHandler, {"path": "."})
], debug=True)

if __name__ == '__main__':
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
