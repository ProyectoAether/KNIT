
![KNITBIO](docs/source/knitbio.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

The KNIT algorithm creates a workflow that aims to detect existing knowledge of a specific domain, collect the most relevant ontologies, study their interconnection, and display the result as a new ontology tailored to the research needs.

This powerful tool streamlines the process of creating ontologies in LifeScience domains.

To perform this function, we need to provide KNIT with the main terms we want to study in our future ontology. With these KeyWords (along with other parameters specified below), KNIT reviews the chosen database (BioPortal, AgroPortal, EcoPortal, MedPortal), selects the most accurate ontologies for us, studies them and creates a new ontology tailored to our needs.

The resulting ontology can be studied in OWL format or visually in the Neo4j database.

## Requirements


### 1. Own a neo4j (can be deployed on Docker)
KNIT uses Neo4j as its database. Download the docker at the following link: https://hub.docker.com/_/neo4j

### 2. It has a user in the target database (BioPortal, AgroPortal, EcoPortal, MedPortal)
Create a user account in the database you want to use (BioPortal, AgroPortal, EcoPortal, MedPortal); the API_KEY will be your user token.

### 3. Create a .env
Create a `.env` file by modifying `.env.template`. Depending on the target base, use the following parameters:

### Database Life Sciences Parameters:
```
-> AgroPortal LIRMM
	REST_URL = http://data.agroportal.lirmm.fr
	sparql_service = http://sparql.agroportal.lirmm.fr/sparql/

-> Bioportal
	REST_URL = http://data.bioontology.org
	sparql_service = http://sparql.bioontology.org/sparql/

-> BioPortal LIRMM (France)
	REST_URL = http://data.bioportal.lirmm.fr
	sparql_service = http://sparql.bioportal.lirmm.fr/sparql/  

-> EcoPortal
	REST_URL = http://ecoportal.lifewatch.eu:8080/
	sparql_service = No data

-> MedPortal
	REST_URL = http://data.medportal.bmicc.cn
	sparql_service = http://sparql.bioontology.org/sparql/
```
The use of BioPortal is recommended.

### REST API Parameters
```
WhiteList -> If you want knitLifeSciencie to USE a specific ontology, you must put the acronym here.

BlackList -> If you want knitLifeSciencie NOT TO USE any ontology, you must put the acronym here

Example to use:

WhiteList = NCIT,MESH,CODO
or
BlackList = NCIT,MESH,CODO
```
### Variables of input csv
```
path_csv -> Input csv address
sep_csv -> Separation used by the csv
```
### Example `.env`
```
#########################################################
# variables of the databases of the bioportal ecosystem #
#########################################################

REST_URL = http://data.bioontology.org
API_KEY = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
sparql_service = http://sparql.bioontology.org/sparql/

#######################################################
# variables of the APIREST of the bioportal ecosystem #
#######################################################

WhiteList =
BlackList =

####################################
# variables of the databases Neo4j #
####################################

IP_SERVER_NEO4J = neo4j://0.0.0.0:7687
USER_NEO4J = xxxxxxxxx
PASSWORD_NEO4J = xxxxxxxxx

##########################
# variables of input csv #
##########################

path_csv = input/test.csv
sep_csv = ,
```

## Getting started
Once the `.env` file is created, modify the `test.csv` file with the keywords. Then install the python requirements:
```
$ pip install -r requeriments.txt
```
And finally, run main.py:
```
$ python3 main.py
```
The final ontology will appear in the output folder with the name `test_o.owl`.
