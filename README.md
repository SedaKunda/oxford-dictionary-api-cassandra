# Oxford-Dictionary-API / Pokemon API
- There are 3 parts to this application. First is the Oxford dictionary API that connects to an Oxford Dictionaries world renowned content. Documentation for this can be found here. https://developer.oxforddictionaries.com/documentation/
- Second, building on top of the pokemon examples worked on in the lab, the app exposes an API with multiple endpoints including POST, PUT, DELETE and GET requests.
- Finally, to explore the creation of my own cassandra database, a keyspace called dictionary is created with 4 tables and exposes some endpoints there as well.

# Overview
The main web app is in /project/dictionary.py and the exposed endpoints are:
- /database/{word} : GET returns the meaning of a word
- /database/synonym/{word} : GET returns the synonyms of a word
- /database/create/{word} : POST creates a new word

- /pokemon/{name} : GET returns attacks for specified name
- /pokemon/types/{type2}/{type1} : GET returns name, type1, type2 for specified type2 and type1
- /pokemon/{type1}/{name} : PUT Update type 1 for specified name
- /pokemon/{type2}/{name} : PUT Update type 2 for specified name
- /pokemon/{name}/delete : DELETE Delete all stats for specified name
- /pokemon/create/{name} : POST creates a new profile with specified name

External API endpoints (i.e. Oxford Dictionary API)
base url= https://od-api.oxforddictionaries.com:443/api/v1/
- /dict/{source_lang}/{word} : GET retrieve dictionary definition for a given word
- /dict/{source_lang}/{word}/example : GET retrieve dictionary examples for a given word
- /dict/{source_lang}/{word}/{region} : GET retrieve dictionary information by region (US or EN)
- /dict/{source_lang}/{word}/synonyms : GET retrieve words that are similar ie synonyms
- /dict/{source_lang}/{word}/synonyms/rare : GET retrieve rare synonyms
- /dict/{source_lang}/{word}/synonyms/dated : GET retrieve dated synonyms
- /languages : GET all languages of oxford dictionaries
- /languages/{reg} : GET language details for specific region
- /languages/dictionary : GET dictionary names for all languages

# Database
Cassandra database was used for storing persistent information. Instructions for setting up the database are below.

# Getting started (setup)
download pokemon.csv file using wget -O pokemon.csv https://tinyurl.com/y25vmgbq

## Queries:
In a container, run kubectl exec -it cassandra-<specific-name> cqlsh and run queries below:
  
```
- CREATE KEYSPACE pokemon WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
- CREATE TABLE pokemon.stats (ID int,Name text PRIMARY KEY, Type1 text, Type2 text, Total int, HP int,Attack int, Defence int, SpAttack int, SpDefence int,Speed int, Generation int, Legendary boolean);
- COPY pokemon.stats(ID,Name,Type1,Type2,Total,HP,Attack,Defence,SpAttack,SpDefence,Speed,Generation,Legendary) FROM '/pokemon.csv' WITH DELIMITER=',' AND HEADER=TRUE;

- CREATE KEYSPACE dictionary WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
- CREATE TABLE dictionary.dictionary (ID int,word text PRIMARY KEY, typeid int, description text, example text);
- CREATE TABLE dictionary.thesaurus (ID int,word text PRIMARY KEY, typeid int,synonym text,example text,subclass int);
- CREATE TABLE dictionary.wordtypes (ID int,type text PRIMARY KEY);
- CREATE TABLE dictionary.synonymtype (ID int,type text PRIMARY KEY);
- insert into dictionary.dictionary (ID,word,typeid,description,example) values (1,'happy',2,'feeling or showing pleasure or contentment','Seda was not happy about the cloud computing assignment');
- insert into dictionary.dictionary (ID,word,typeid,description,example) values (2,'sad',2,'feeling or showing sorrow','he was crying because he was sad');
- insert into dictionary.dictionary (ID,word,typeid,description,example) values (3,'work',1,'activity involving mental or physical effort done in order to achieve a purpose or result','tired from a days work');
- insert into dictionary.dictionary (ID,word,typeid,description,example) values (4,'walk',1,'move at a regular pace by lifting and setting down each foot in turn never having both feet off the ground at once','take the dog for a walk');
- insert into dictionary.dictionary (ID,word,typeid,description,example) values (5,'glass',3,'a drinking container made from glass','a beer glass');
- insert into dictionary.thesaurus (ID,word,typeid,synonym,example,subclass) values (1,'happy',2,'thrilled','Seda was not thrilled about the cloud computing assignment',3);
- insert into dictionary.thesaurus (ID,word,typeid,synonym,example,subclass) values (2,'sad',2,'despondent','he was crying because he was despondent',1);
- insert into dictionary.thesaurus (ID,word,typeid,synonym,example,subclass) values (3,'work',1,'toil','tired from a days toil',1);
- insert into dictionary.thesaurus (ID,word,typeid,synonym,example,subclass) values (4,'walk',1,'saunter','take the dog for a saunter',2);
- insert into dictionary.thesaurus (ID,word,typeid,synonym,example,subclass) values (5,'glass',3,'mirror','she couldnt wait to put the dress on and look in the glass',3);
- insert into dictionary.wordtypes (ID,type) values (1,'verb');
- insert into dictionary.wordtypes (ID,type) values (2,'adjectives');
- insert into dictionary.wordtypes (ID,type) values (3,'noun');
- insert into dictionary.synonymtype (ID,type) values (1,'rare');
- insert into dictionary.synonymtype (ID,type) values (2,'dated');
- insert into dictionary.synonymtype (ID,type) values (3,'regular');
```
# Deployment
This application is created for the Kubertenes environment. The following steps must be followed for deployment (in order).

- kubectl create -f cassandra-peer-service.yaml 
- kubectl create -f cassandra-service.yaml 
- kubectl create -f cassandra-replication-controller.yaml 
- kubectl create -f frontend-deployment.yaml 
- kubectl create -f frontend-service.yaml 

## To scale:
> kubectl scale deployment project --replicas=3

> kubectl scale rc cassandra --replicas=3

# Authors
Seda Kunda
