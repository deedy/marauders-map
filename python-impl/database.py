import redis
import cPickle as pickle
import time
import random

millsecond_length_of_tail = 1000*60*30 # half an hour
current_milli_time = lambda: int(round(time.time() * 1000))
defaultlat = 37.331703
defaultlng = -122.030240
loop = [(37.33054 , -122.02969) , (37.33054 , -122.02971), (37.33054 , -122.02975), (37.33054 , -122.02977), (37.33054 , -122.02980), (37.33054 , -122.02982), (37.33054 , -122.02987), (37.33054 , -122.02990), (37.33054 , -122.02992), (37.33054 , -122.02995), (37.33054 , -122.02999), (37.33054 , -122.03002), (37.33054 , -122.03003), (37.33054 , -122.03005), (37.33054 , -122.03008), (37.33054 , -122.03011), (37.33054 , -122.03014), (37.33054 , -122.03017), (37.33054 , -122.03019), (37.33054 , -122.03022), (37.33054 , -122.03024), (37.33054 , -122.03027), (37.33054 , -122.03030), (37.33054 , -122.03033), (37.33054 , -122.03035), (37.33054 , -122.03037), (37.33054 , -122.03039), (37.33053 , -122.03045), (37.33053 , -122.03048), (37.33052 , -122.03054), (37.33054 , -122.03055), (37.33056 , -122.03055), (37.33058 , -122.03056), (37.33060 , -122.03057), (37.33063 , -122.03058), (37.33066 , -122.03059), (37.33068 , -122.03060), (37.33071 , -122.03061), (37.33074 , -122.03062), (37.33078 , -122.03062), (37.33080 , -122.03064), (37.33082 , -122.03064), (37.33084 , -122.03065), (37.33086 , -122.03066), (37.33089 , -122.03066), (37.33091 , -122.03067), (37.33093 , -122.03068), (37.33095 , -122.03069), (37.33097 , -122.03070), (37.33100 , -122.03070), (37.33102 , -122.03071), (37.33104 , -122.03072), (37.33107 , -122.03073), (37.33108 , -122.03073), (37.33110 , -122.03074), (37.33112 , -122.03074), (37.33113 , -122.03075), (37.33115 , -122.03075), (37.33117 , -122.03076), (37.33119 , -122.03076), (37.33120 , -122.03076), (37.33121 , -122.03076), (37.33123 , -122.03076), (37.33125 , -122.03076), (37.33126 , -122.03075), (37.33128 , -122.03075), (37.33130 , -122.03075), (37.33132 , -122.03075), (37.33135 , -122.03075), (37.33138 , -122.03075), (37.33139 , -122.03075), (37.33140 , -122.03075), (37.33143 , -122.03075), (37.33145 , -122.03075), (37.33146 , -122.03075), (37.33149 , -122.03075), (37.33151 , -122.03075), (37.33153 , -122.03075), (37.33156 , -122.03075), (37.33158 , -122.03075), (37.33161 , -122.03075), (37.33163 , -122.03075), (37.33165 , -122.03075), (37.33167 , -122.03075), (37.33168 , -122.03075), (37.33170 , -122.03075), (37.33173 , -122.03075), (37.33175 , -122.03075), (37.33176 , -122.03075), (37.33177 , -122.03075), (37.33179 , -122.03075), (37.33182 , -122.03075), (37.33184 , -122.03075), (37.33187 , -122.03075), (37.33189 , -122.03075), (37.33190 , -122.03075), (37.33193 , -122.03075), (37.33195 , -122.03075), (37.33199 , -122.03075), (37.33202 , -122.03075), (37.33204 , -122.03074), (37.33207 , -122.03075), (37.33210 , -122.03075), (37.33213 , -122.03075), (37.33215 , -122.03075), (37.33218 , -122.03075), (37.33220 , -122.03075), (37.33223 , -122.03075), (37.33225 , -122.03075), (37.33230 , -122.03075), (37.33233 , -122.03075), (37.33237 , -122.03074), (37.33240 , -122.03075), (37.33245 , -122.03075), (37.33248 , -122.03075), (37.33251 , -122.03074), (37.33256 , -122.03076), (37.33259 , -122.03074), (37.33263 , -122.03075), (37.33266 , -122.03075), (37.33270 , -122.03074), (37.33275 , -122.03074), (37.33278 , -122.03074), (37.33281 , -122.03073), (37.33284 , -122.03072), (37.33287 , -122.03071), (37.33288 , -122.03071), (37.33291 , -122.03069), (37.33294 , -122.03067), (37.33297 , -122.03066), (37.33300 , -122.03064), (37.33303 , -122.03062), (37.33306 , -122.03060), (37.33309 , -122.03058), (37.33312 , -122.03055), (37.33314 , -122.03053), (37.33317 , -122.03050), (37.33319 , -122.03047), (37.33322 , -122.03045), (37.33325 , -122.03042), (37.33327 , -122.03039), (37.33329 , -122.03036), (37.33330 , -122.03032), (37.33334 , -122.03028), (37.33337 , -122.03021), (37.33340 , -122.03015), (37.33343 , -122.03007), (37.33345 , -122.02999), (37.33347 , -122.02990), (37.33349 , -122.02981), (37.33349 , -122.02974), (37.33349 , -122.02967), (37.33349 , -122.02959), (37.33349 , -122.02953), (37.33348 , -122.02948), (37.33347 , -122.02942), (37.33347 , -122.02936), (37.33344 , -122.02925), (37.33342 , -122.02920), (37.33340 , -122.02916), (37.33339 , -122.02912), (37.33337 , -122.02908), (37.33335 , -122.02905), (37.33333 , -122.02902), (37.33332 , -122.02898), (37.33330 , -122.02896), (37.33328 , -122.02893), (37.33326 , -122.02890), (37.33324 , -122.02888), (37.33322 , -122.02886), (37.33321 , -122.02884), (37.33319 , -122.02882), (37.33317 , -122.02879), (37.33315 , -122.02878), (37.33313 , -122.02876), (37.33311 , -122.02874), (37.33309 , -122.02873), (37.33307 , -122.02871), (37.33305 , -122.02870), (37.33303 , -122.02869), (37.33301 , -122.02867), (37.33298 , -122.02866), (37.33296 , -122.02865), (37.33294 , -122.02863), (37.33291 , -122.02862), (37.33289 , -122.02861), (37.33286 , -122.02860), (37.33283 , -122.02859), (37.33281 , -122.02858), (37.33278 , -122.02858), (37.33276 , -122.02858), (37.33274 , -122.02857), (37.33270 , -122.02857), (37.33264 , -122.02856), (37.33259 , -122.02856), (37.33253 , -122.02856), (37.33248 , -122.02856), (37.33243 , -122.02856), (37.33239 , -122.02855), (37.33234 , -122.02856), (37.33230 , -122.02855), (37.33221 , -122.02856), (37.33211 , -122.02856), (37.33204 , -122.02856), (37.33198 , -122.02856), (37.33193 , -122.02856), (37.33188 , -122.02856), (37.33184 , -122.02856), (37.33182 , -122.02856), (37.33180 , -122.02856), (37.33177 , -122.02856), (37.33175 , -122.02856), (37.33173 , -122.02856), (37.33170 , -122.02856), (37.33168 , -122.02856), (37.33163 , -122.02856), (37.33158 , -122.02856), (37.33151 , -122.02856), (37.33146 , -122.02856), (37.33140 , -122.02856), (37.33135 , -122.02855), (37.33130 , -122.02856), (37.33124 , -122.02856), (37.33118 , -122.02856), (37.33113 , -122.02856), (37.33108 , -122.02856), (37.33103 , -122.02856), (37.33098 , -122.02856), (37.33093 , -122.02857), (37.33088 , -122.02859), (37.33081 , -122.02861), (37.33076 , -122.02865), (37.33070 , -122.02870), (37.33065 , -122.02876), (37.33062 , -122.02883), (37.33058 , -122.02890), (37.33054 , -122.02898), (37.33054 , -122.02901), (37.33054 , -122.02905), (37.33054 , -122.02909), (37.33055 , -122.02913), (37.33054 , -122.02918), (37.33054 , -122.02922), (37.33054 , -122.02925), (37.33054 , -122.02930), (37.33054 , -122.02935), (37.33054 , -122.02939), (37.33054 , -122.02942), (37.33054 , -122.02949), (37.33054 , -122.02953), (37.33054 , -122.02957), (37.33054 , -122.02961), (37.33054 , -122.02965), (37.33054 , -122.02968), (37.33056 , -122.02968), (37.33059 , -122.02968), (37.33062 , -122.02968), (37.33065 , -122.02968), (37.33068 , -122.02968), (37.33070 , -122.02968), (37.33074 , -122.02968), (37.33077 , -122.02968), (37.33080 , -122.02968), (37.33085 , -122.02967), (37.33089 , -122.02967), (37.33094 , -122.02967), (37.33100 , -122.02967), (37.33105 , -122.02967), (37.33112 , -122.02967), (37.33114 , -122.02967), (37.33118 , -122.02966), (37.33123 , -122.02966), (37.33127 , -122.02966), (37.33132 , -122.02966), (37.33135 , -122.02966), (37.33139 , -122.02966), (37.33144 , -122.02964), (37.33149 , -122.02963), (37.33153 , -122.02961), (37.33157 , -122.02959), (37.33163 , -122.02958), (37.33164 , -122.02964), (37.33165 , -122.02971), (37.33167 , -122.02975), (37.33171 , -122.02981), (37.33176 , -122.02984), (37.33182 , -122.02986), (37.33188 , -122.02986), (37.33193 , -122.02985), (37.33198 , -122.02981), (37.33202 , -122.02975), (37.33205 , -122.02969), (37.33206 , -122.02962), (37.33206 , -122.02955), (37.33206 , -122.02949), (37.33202 , -122.02943), (37.33198 , -122.02937), (37.33191 , -122.0293)] ;
r = redis.Redis()

def map_id_exists(map_id):
	map_exists = r.sismember("map_ids", map_id)
	return map_exists

def get_map_ids():
    map_ids = r.smembers("map_ids")
    return map_ids

def get_map_info(map_id):
	map_key = "map:%s" % map_id
	map_info_pickle_dict = r.get(map_key)
	if map_info_pickle_dict == None:
		return None
	map_info_dict = pickle.loads(map_info_pickle_dict)
	return map_info_dict # ["map_id", "map_name", "created"]

def get_map_infos():
	map_ids = get_map_ids()
	pipe = r.pipeline()
	for map_id in map_ids:
		map_key = "map:%s" % map_id
		pipe.get(map_key)
	map_arrs = pipe.execute()
	map_infos = map(pickle.loads, map_arrs)
	return map_infos

def get_new_map_id():
	new_map_id = r.incr("map_id_counter")
	return new_map_id

def create_new_map(map_name, lat = defaultlat, lng = defaultlng):
	new_map_id = get_new_map_id()
	map_dict = {
		"map_id" : new_map_id,
		"map_name" : map_name,
		"created" : current_milli_time(),
		"lat" : lat,
		"lng" : lng,
	}
	map_key = "map:%s" % new_map_id
	r.set(map_key, pickle.dumps(map_dict))
	r.sadd("map_ids", new_map_id)
	return new_map_id

def delete_map(map_id):
	map_key = "map:%s" % map_id
	r.srem("map_ids", map_id)

	players_in_map = get_player_ids_for_map(map_id)
	pipe = r.pipeline()
	for player_id in players_in_map:
		players_map_key = "players:%s:maps" % player_id
		pipe.srem(players_map_key, map_id)
	map_players_key = "maps:%s:players" % map_id
	pipe.delete(map_players_key)
	pipe.delete("map:%s" % map_id)
	pipe.execute()

def player_id_exists(player_id):
	player_exists = r.sismember("player_ids", player_id)
	return player_exists

def get_player_ids():
	player_ids = r.smembers("player_ids")
	return player_ids

def get_player_info(player_id):
	player_key = "players:%s" % player_id
	player_info_pickle_dict = r.get(player_key)
	if player_info_pickle_dict == None:
		return
	player_info_dict = pickle.loads(player_info_pickle_dict)
	return player_info_dict # ["player_id", "player_name", "created"]

def get_player_infos():
	player_ids = get_player_ids()
	pipe = r.pipeline()
	for player_id in player_ids:
		player_key = "player:%s" % player_id
		pipe.get(player_key)
	player_arrs = pipe.execute()
	player_infos = map(pickle.loads, player_arrs)
	return player_infos

def get_new_player_id():
	new_player_id = r.incr("player_id_counter")
	return new_player_id

def create_new_player(player_name):
	new_player_id = get_new_player_id()
	player_dict = {
		"player_id" : new_player_id,
		"player_name" : player_name,
		"created" : current_milli_time()
	}
	player_key = "player:%s" % new_player_id
	r.set(player_key, pickle.dumps(player_dict))
	r.sadd("player_ids", new_player_id)
	return new_player_id

def delete_player(player_id):
	player_key = "player:%s" % player_id
	r.srem("player_ids", player_id)
	r.delete(player_key)

	maps_in_player = get_map_ids_for_player(player_id)
	pipe = r.pipeline()
	for map_id in maps_in_player:
		map_players_key = "maps:%s:players" % map_id
		pipe.srem(map_players_key, player_id)
	pipe.delete("players:%s" % player_id)
	pipe.delete("players:%s:maps" % player_id)
	pipe.delete("player:%s:location" % player_id)
	pipe.execute()

def update_location(player_id, lat, lng):
	if not player_id_exists(player_id):
		return
	timestamp = current_milli_time()
	location_dict = {
		"lat" : lat,
		"lng" : lng,
		"created" : timestamp
	}
	player_loc_key = "player:%s:location" % player_id
	r.zadd(player_loc_key, pickle.dumps(location_dict), timestamp)

def add_player_to_map(map_id, player_id):
	if not map_id_exists(map_id):
		return
	if not player_id_exists(player_id):
		return
	map_players_key = "maps:%s:players" % map_id
	r.sadd(map_players_key, player_id)
	players_map_key = "players:%s:maps" % player_id
	r.sadd(players_map_key, map_id)

def get_map_ids_for_player(player_id):
	map_ids = r.smembers('players:%s:maps' % player_id)
	return map_ids

def get_map_infos_for_player(player_id):
	map_ids = get_map_ids_for_player(player_id)
	pipe = r.pipeline()
	for map_id in map_ids:
		map_key = "map:%s" % map_id
		pipe.get(map_key)
	map_arrs = pipe.execute()
	map_infos = map(pickle.loads, map_arrs)
	return map_infos

def get_player_ids_for_map(map_id):
	player_ids = r.smembers('maps:%s:players' % map_id)
	return player_ids

def get_player_infos_for_map(map_id):
	player_ids = get_player_ids_for_map(map_id)
	pipe = r.pipeline()
	for player_id in player_ids:
		player_key = "player:%s" % player_id
		pipe.get(player_key)
	player_arrs = pipe.execute()
	player_infos = map(pickle.loads, player_arrs)
	return player_infos

def get_player_locations(player_id, tail_length = millsecond_length_of_tail):
	player_loc_key = "player:%s:location" % player_id
	until_timestamp = current_milli_time() - tail_length
	player_tail = r.zrevrangebyscore(player_loc_key, '+inf', until_timestamp)
	player_tail = map(pickle.loads, player_tail)
	return player_tail

def get_players_locations_for_map(map_id, tail_length = millsecond_length_of_tail):
    player_ids = get_player_ids_for_map(map_id)
    until_timestamp = current_milli_time() - tail_length
    pipe = r.pipeline()
    for player_id in player_ids:
        player_loc_key = "player:%s:location" % player_id
        pipe.zrevrangebyscore(player_loc_key, '+inf', until_timestamp)
    player_arrs = pipe.execute()
    player_locations = []
    for player_arr in player_arrs:
        player_locations.append(map(pickle.loads, player_arr))
    return zip(player_ids,player_locations)


# Create 4 players and 2 games
# Add the first 3 players to game 1
# and the last 3 players to game 2
# Give each of the players 3 unique locations
def test_script():
	r.flushall()
	create_new_player("Theodoros") #Gkountouvas
	create_new_player("Ken Birman")
	create_new_player("Deedy Das")
	create_new_player("Dominick Twitty")
	create_new_map("Anarchists", 37.331703, -122.030240)
	create_new_map("Chinese Democracy", 37.331703, -122.030240)
	add_player_to_map(1,1)
	add_player_to_map(1,2)
	add_player_to_map(2,3)
	add_player_to_map(2,4)
	add_player_to_map(1,3)
	add_player_to_map(2,2)
	update_location(1,defaultlat-0.002,defaultlng-0.003)
	update_location(1,defaultlat-0.001,defaultlng-0.003)
	update_location(1,defaultlat,defaultlng-0.003)
	update_location(2,defaultlat-0.002,defaultlng-0.001)
	update_location(2,defaultlat-0.001,defaultlng-0.001)
	update_location(2,defaultlat,defaultlng-0.001)
	update_location(3,defaultlat-0.002,defaultlng+0.001)
	update_location(3,defaultlat-0.001,defaultlng+0.001)
	update_location(3,defaultlat,defaultlng+0.001)
	update_location(4,defaultlat-0.002,defaultlng+0.003)
	update_location(4,defaultlat-0.001,defaultlng+0.003)
	update_location(4,defaultlat,defaultlng+0.003)

def create_random_path(player_id):
	update_location(player_id,defaultlat,defaultlng)
	lastlat = defaultlat
	lastlng = defaultlng
	dirone = (random.random() - 0.5)/5
	dirtwo = (random.random() - 0.5)/5
	for i in xrange(20):
		delta_lat = (random.normalvariate(dirone, 0.05) )/ 1000
		delta_lng = (random.normalvariate(dirtwo, 0.05) )/ 1000
		lastlat += delta_lat
		lastlng += delta_lng
		update_location(player_id,lastlat,lastlng)

def simulate_loop():
	return loop
