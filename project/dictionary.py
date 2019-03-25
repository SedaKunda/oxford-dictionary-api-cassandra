from flask import Flask, render_template, request, jsonify
import json
import requests
import requests_cache
from cassandra.cluster import Cluster

#enable automatic caching
requests_cache.install_cache('dictionary_cache', backend='sqlite', expire_after=15000)

#connect to cassandra db and pokemon keyspace
cluster = Cluster(['cassandra'])
session = cluster.connect()

app = Flask(__name__, instance_relative_config=True)
#config file contains api key and api id
app.config.from_pyfile('config.py')

# base URL for Oxford Dictionary API
base_url='https://od-api.oxforddictionaries.com:443/api/v1/'

#alternative endpoint URLs
all_entries_url='{base_url}entries/{source_lang}/{word}'
syn_entries_url='{base_url}entries/{source_lang}/{word}/synonyms'
reg_entries_url='{base_url}entries/{source_lang}/{word}/regions={region}'
languages_url = '{base_url}languages'

#set API keys
key = app.config['APP_KEY']
_id = app.config['APP_ID']

#appliation route goes to external html file
@app.route('/')
def hello():
	return render_template('index.html')

#######PERSISTENT CLOUD DATABASE
###cassandra
#get attacks for specified name
@app.route('/pokemon/<name>', methods=['GET'])
def profile(name):
	rows = session.execute("Select attack, name From pokemon.stats where name = '{}' ALLOW FILTERING".format(name))
	dict_name = {}
	if not rows:
		return jsonify({'error':'No pokemons with that name'}), 404
	else:
		for (attack, name) in rows:
			dict_name[name] = attack
		return jsonify(dict_name), 200

#get name, type1, type2 for specified type2 and type1
@app.route('/pokemon/types/<type2>/<type1>', methods=['GET'])
def profile_type(type2, type1):
	rows = session.execute("Select type1, type2, name From pokemon.stats where type2 = '{}' and type1 = '{}' ALLOW FILTERING".format(type2, type1))
	dict_t2 = {}
	if not rows:
		return jsonify({'error':'No pokemons with that Type 2 and Type 1 combination'}), 404
	else:
		for (type1, type2, name) in rows:
			dict_t2[name] = (type2,type1)
		return jsonify(dict_t2), 200

#create a new profile with specified name
@app.route('/pokemon/<name>', methods=['POST'])
def create_profile(name):
	if not request.form or not 'name' in request.form: #check if request is json format and has a name
		return jsonify({'error':'the new record needs to have a name'}), 400
	else:
		name = request.form['name']
		rows = session.execute("Insert into pokemon.stats (Name,Type1,Type2,Total,HP,Attack,Defence,SpAttack,SpDefence,Speed,Generation,Legendary) values('{}','sometype','sometype',2,3,4,5,6,7,8,9,True)".format(name))
		return jsonify({'created':' /pokemon/{}'.format(name)}), 201

#Update type 1 for specified name
@app.route('/pokemon/<type1>/<name>', methods=['POST', 'PUT'])
def update_profile_type1(type1, name):
	if not request.form or not 'name' in request.form: #check if request is json format and has a name
		return jsonify({'error':'the new record needs to have a name'}), 400
	else:
		if request.method == 'POST':
			type1 = request.form['type1']
			name = request.form['name']
		rows = session.execute("update pokemon.stats set type1 = '{}' where name = '{}'".format(type1,name))
		return jsonify({'updated':'to /pokemon/{}/{}'.format(name, type1)}), 201

#Update type 2 for specified name
@app.route('/pokemon/<type2>/<name>', methods=['POST', 'PUT'])
def update_profile_type2(type2, name):
	if not request.form or not 'name' in request.form: #check if request is json format and has a name
		return jsonify({'error':'the new record needs to have a name'}), 400
	else:
		if request.method == 'POST':
			type2 = request.form['type2']
			name = request.form['name']
		rows = session.execute("update pokemon.stats set type2 = '{}' where name = '{}'".format(type2,name))
		return jsonify({'updated':'to /pokemon/{}/{}'.format(name, type2)}), 201

#Delete all stats for specified name
@app.route('/pokemon/<name>/delete', methods=['POST', 'DELETE'])
def delete_profile(name):
	if not request.form or not 'name' in request.form: #check if request is json format and has a title
		return jsonify({'error':'the record needs to have a name'}), 400
	else:
		if request.method == 'POST':
			name = request.form['name']
		rows = session.execute("delete from pokemon.stats where name = '{}'".format(name))
		return jsonify({'deleted':' /pokemon/{}'.format(name)}), 201

#######EXTERNAL API
###ALL METHODS RELATED TO DICTIONARY
#retrieve dictionary definition for a given word
@app.route('/dict/<source_lang>/<word>', methods=['GET', 'POST'])
def get_word_definition(source_lang, word):
	if request.method == 'POST':
		src = request.form['src']
		wrd = request.form['wrd']
	full_url = all_entries_url.format(base_url=base_url, source_lang=src, word=wrd)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response_trimmed = [x['definitions'] for x in response['results'][0]['lexicalEntries'][0]['entries'][0]['senses']]
		return jsonify(response_trimmed), 200
	else:
		return resp.reason, 404

#retrieve dictionary examples for a given word
@app.route('/dict/<source_lang>/<word>/example', methods=['GET', 'POST'])#word must bbe lowercase
def get_word_example(source_lang, word):
	if request.method == 'POST':
		src = request.form['src']
		wrd = request.form['wrd']
	full_url = all_entries_url.format(base_url=base_url, source_lang=src, word=wrd)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response_trimmed = [x['examples'] for x in response['results'][0]['lexicalEntries'][0]['entries'][0]['senses']]
		return jsonify(response_trimmed), 200
	else:
		return resp.reason, 404

#retrieve dictionary information by region (US or EN)
@app.route('/dict/<source_lang>/<word>/<region>', methods=['GET', 'POST'])
def get_word_by_region(source_lang, word, region):
	if request.method == 'POST':
		src = request.form['src']
		wrd = request.form['wrd']
		reg = request.form['reg']
	full_url = reg_entries_url.format(base_url=base_url, source_lang=src, word=wrd, region=reg)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response_trimmed = [x for x in response['results'][0]['lexicalEntries'][0]['entries']]
		return jsonify(response_trimmed), 200
	else:
		return resp.reason, 404

###ALL METHODS RELATED TO SYNONYMS
#retrieve words that are similar ie synonyms
@app.route('/dict/<source_lang>/<word>/synonyms', methods=['GET', 'POST'])
def get_synonyms(source_lang, word):
	if request.method == 'POST':
		src = request.form['src']
		wrd = request.form['wrd']
	full_url = syn_entries_url.format(base_url=base_url, source_lang=src, word=wrd)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response_trimmed = [x['synonyms'] for x in response['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['subsenses']]
		return jsonify(response_trimmed), 200
	else:
		return resp.reason, 404

#retrieve rare synonyms
@app.route('/dict/<source_lang>/<word>/synonyms/rare', methods=['GET', 'POST'])
def get_synonyms_rare(source_lang, word):
	if request.method == 'POST':
		src = request.form['src']
		wrd = request.form['wrd']
	full_url = syn_entries_url.format(base_url=base_url, source_lang=src, word=wrd)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response_trimmed = [x['synonyms'] for x in response['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['subsenses'] if 'registers' in x and x['registers'][0]== 'rare']
		return jsonify(response_trimmed), 200
	else:
		return resp.reason, 404

#retrieve dated synonyms
@app.route('/dict/<source_lang>/<word>/synonyms/dated', methods=['GET', 'POST'])
def get_synonyms_dated(source_lang, word):
	if request.method == 'POST':
		src = request.form['src']
		wrd = request.form['wrd']
	full_url = syn_entries_url.format(base_url=base_url, source_lang=src, word=wrd)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response_trimmed = [x['synonyms'] for x in response['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][0]['subsenses'] if 'registers' in x and x['registers'][0]== 'dated']
		return jsonify(response_trimmed), 200
	else:
		return resp.reason, 404

###ALL METHODS RELATED TO LANGUAGE
#all languages of oxford dictionaries
@app.route('/languages', methods=['GET'])
def get_all_languages():
	full_url = languages_url.format(base_url=base_url)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		return jsonify(response), 200
	else:
		return resp.reason, 404

#language details for specific region
@app.route('/languages/<reg>', methods=['GET', 'POST'])
def get_language_by_region(reg):
	if request.method == 'POST':
		reg = request.form['reg']
	full_url = languages_url.format(base_url=base_url)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response2 = [ x for x in response['results'] if 'region' in x and x['region'] == reg]
		return jsonify(response2), 200
	else:
		return resp.reason, 404

#dictionary names for all languages
@app.route('/languages/dictionary', methods=['GET'])
def get_language_dictionaries():
	full_url = languages_url.format(base_url=base_url)
	resp = requests.get(full_url, headers={'app_key' : key, 'app_id' : _id})
	if resp.ok:
		response = resp.json()
		response2 = {x['source'] : '' for x in response['results']}
		return jsonify(response2), 200
	else:
		return resp.reason, 404

if __name__=="__main__":
    app.run(port=8080, debug=True)
#   app.run(port=8080, debug=True, ssl_context='adhoc') #ssl context enables running over https
#   app.run(port=8080, debug=True, ssl_context=('cert.pem', 'key.pem')) #for self signed ssl certficate
