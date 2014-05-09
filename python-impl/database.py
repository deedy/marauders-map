import redis

r = redis.Redis()

map_fields = ["map_id", "map_name"]

def map_id_exists(map_id):
	map_exists = r.sismember("map_ids", map_id)
	return exists

def get_map_ids():
    map_ids = r.smembers("map_ids")
    return map_ids

def map_to_dict(map_arr):
	map_dict = dict(zip(map_fields, map_arr))
	return map_dict

def get_map_info(map_id):
	map_key = "maps:%s" % map_id
	map_arr = r.hmget(map_key, map_fields)
	map_info = map_to_dict(map_arr)
	return map_info

def get_map_infos():
	map_ids = get_map_ids()
	pipe = r.pipeline()
	for map_id in map_ids:
		map_key = "maps:%s" % map_id
		pipe.hmget(map_key, map_fields)
	map_arrs = pipe.execute()
	map_infos = map(map_to_dict, map_arrs)
	return map_infos

def get_new_map_id():
	new_map_id = r.incr("map_id_counter")
	return new_map_id

def add_map(map_id, map_dict):
	map_key = "maps:%s" % map_id
	r.hmset(map_key, map_dict)
	r.sadd("map_ids", map_id)

def create_new_map(map_name):
	new_map_id = get_new_map_id()
	map_dict = dict(zip(map_fields, [new_map_id, map_name]))
	add_map(new_map_id, map_dict)
	return new_map_id

def delete_map(map_id):
	map_key = "maps:%s" % map_id
	r.srem("map_ids", map_id)
	r.delete(map_key)
	delete_players(map_id)

player_fields = ["player_id", "player_name", "lat", "lng"]

def player_id_exists(map_id, player_id):
	player_set_key = "maps:%s:players" % map_id
	player_exists = r.sismember(player_set_key, player_id)
	return player_exists

def get_player_ids(map_id):
	player_set_key = "maps:%s:players" % map_id
	player_ids = r.smembers(player_set_key)
	return player_ids

def player_to_dict(player_arr):
	player_dict = dict(zip(player_fields, player_arr))
	return player_dict

def get_player_info(map_id, player_id):
	player_key = "maps:%s:players:%s" % (map_id, player_id)
	player_arr = r.hmget(player_key, player_fields)
	player_info = player_to_dict(player_arr)
	return player_info

def get_player_infos(map_id):
	player_ids = get_player_ids(map_id)
	pipe = r.pipeline()
	for player_id in player_ids:
		player_key = "maps:%s:players:%s" % (map_id, player_id)
		pipe.hmget(player_key, player_fields)
	player_arrs = pipe.execute()
	player_infos = map(player_to_dict, player_arrs)
	return player_infos

def get_new_player_id(map_id):
	map_counter_key = "maps:%s:player_id_counter" % map_id
	new_player_id = r.incr(map_counter_key)
	return new_player_id

def add_player(map_id, player_id, player_dict):
	map_key = "maps:%s" % map_id
	player_set_key = map_key + ":players"
	player_key = player_set_key + (":%s" % player_id)
	r.hmset(player_key, player_dict)
	r.sadd(player_set_key, player_id)

def create_new_player(map_id, player_name):
	new_player_id = get_new_player_id(map_id)
	player_data = [new_player_id, player_name, "null", "null"]
	player_dict = dict(zip(player_fields, player_data))
	add_player(map_id, new_player_id, player_dict)
	return new_player_id

def delete_player(map_id, player_id):
	map_key = "maps:%s" % map_id
	player_set_key = map_key + ":players"
	player_key = player_set_key + (":%s" % player_id)
	r.srem(player_set_key, player_id)
	r.delete(player_key)

def delete_players(map_id):
	map_key = "maps:%s" % map_id
	player_set_key = map_key + ":players"
	player_ids = get_player_ids(map_id)
	r.delete(player_set_key)
	for player_id in player_ids:
		player_key = player_set_key + (":%s" % player_id)
		r.delete(player_key)

def update_location(map_id, player_id, lat, lng):
	player_key = "maps:%s:players:%s" % (map_id, player_id)
	update_dict = dict(zip(["lat", "lng"], [lat, lng]))
	r.hmset(player_key, update_dict)
