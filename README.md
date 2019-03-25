# Oxford-Dictionary-API / Pokemon API
- This application uses pokemon.csv data stored in a cassandra database as its main domain and makes use of the Oxford Dictionary API to complement it's functionality.
- Cloud computing coursework.

# Overview
The main web app is in /project/dictionary.py and the exposed endpoints are:

- /pokemon/{name} : GET returns attacks for specified name
- /pokemon/types/{type2}/{type1} : GET returns name, type1, type2 for specified type2 and type1
- /pokemon/{type1}/{name} : PUT Update type 1 for specified name
- /pokemon/{type2}/{name} : PUT Update type 2 for specified name
- /pokemon/{name}/delete : DELETE Delete all stats for specified name
- /pokemon/create/{name} : POST creates a new profile with specified name

External API endpoints (i.e. Oxford Dictionary API)
base url= https://od-api.oxforddictionaries.com:443/api/v1/
- /dict/<source_lang>/<word> : GET retrieve dictionary definition for a given word
- /dict/<source_lang>/<word>/example : GET retrieve dictionary examples for a given word
- /dict/<source_lang>/<word>/<region> : GET retrieve dictionary information by region (US or EN)
- /dict/<source_lang>/<word>/synonyms : GET retrieve words that are similar ie synonyms
- /dict/<source_lang>/<word>/synonyms/rare : GET retrieve rare synonyms
- /dict/<source_lang>/<word>/synonyms/dated : GET retrieve dated synonyms
- /languages : GET all languages of oxford dictionaries
- /languages/<reg> : GET language details for specific region
- /languages/dictionary : GET dictionary names for all languages

# Getting started
download pokemon.csv file using wget -O pokemon.csv https://tinyurl.com/y25vmgbq

QUERIES:
In container, run kubectl exec -it cassandra-<specific-name> cqlsh and run queries below
CREATE KEYSPACE pokemon WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
CREATE TABLE pokemon.stats (ID int,Name text PRIMARY KEY, Type1 text, Type2 text, Total int, HP int,Attack int, Defence int, SpAttack int, SpDefence int,Speed int, Generation int, Legendary boolean);
COPY pokemon.stats(ID,Name,Type1,Type2,Total,HP,Attack,Defence,SpAttack,SpDefence,Speed,Generation,Legendary) FROM '/pokemon.csv' WITH DELIMITER=',' AND HEADER=TRUE;

# Deployment
This application is created for the Kubertenes environment.

# Prerequisites

# Authors
Seda Kunda

# Acknowledgments
Arman Khouzani
