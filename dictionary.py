from flask import Flask, render_template, request, jsonify
from json2html import *
import json
import requests
import requests_cache

#enable automatic caching
requests_cache.install_cache('dictionary_cache', backend='sqlite', expire_after=15000)

app = Flask(__name__, instance_relative_config=True)

#config file contains api key and api id
app.config.from_object('config')
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

###ALL METHODS RELATED TO DICTIONARY
#retrieve dictionary definition for a given word
@app.route('/<source_lang>/<word>', methods=['GET', 'POST'])#word must bbe lowercase
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
@app.route('/<source_lang>/<word>/example', methods=['GET', 'POST'])#word must bbe lowercase
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
@app.route('/<source_lang>/<word>/<region>', methods=['GET', 'POST'])
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
		return json2html.convert(json = response_trimmed), 200
	else:
		return resp.reason, 404

###ALL METHODS RELATED TO SYNONYMS
#retrieve words that are similar ie synonyms
@app.route('/<source_lang>/<word>/synonyms', methods=['GET', 'POST'])
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
@app.route('/<source_lang>/<word>/synonyms/rare', methods=['GET', 'POST'])
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
@app.route('/<source_lang>/<word>/synonyms/dated', methods=['GET', 'POST'])
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
		return json2html.convert(json = response), 200
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
    app.run(port=8080, debug=True, ssl_context='adhoc') #ssl context enables running over https
#   app.run(port=8080, debug=True, ssl_context=('cert.pem', 'key.pem')) #for self signed ssl certficate
