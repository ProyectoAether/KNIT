# KNIT

The KNIT algorithm creates a workflow that aims to detect the existing knowledge of a specific domain, collect the most relevant ontologies, study their interconnection and display the result as a new ontology adjusted to the research needs.

With this idea, the KnitBio tool is developed.

![KNITBIO](docs/source/knitbio.svg)

KnitBio is a powerful tool designed to streamline the process of creating ontologies in LifeScience domains using the KNIT algorithm. To do this, it uses ontologies already made in the Bioportal, AgroPortal, EcoPortal or MedPortal.
To perform this function, we must provide the tools with the main terms we want to study in our future ontology. With this data (along with other parameters specified in the operation section), KnitBio reviews the chosen database (BioPortal, AgroPortal, EcoPortal, MedPortal), selecting the most accurate ontologies for the input terms.
This ontology can be studied in OWL format or visually in the Neo4j database.

## Requirements

---
---
# Data .env

## Database Life Sciences Parameters:
    
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
            REST_URL = 
            sparql_service = No data

        -> MedPortal
            REST_URL = http://data.medportal.bmicc.cn
            sparql_service = http://sparql.bioontology.org/sparql/

## REST API Parameters

        wc -> Weight assigned to the ontology coverage criterion.
        wa -> Weight assigned to the ontology acceptance criterion.
        wd -> Weight assigned to the ontology detail criterion.
        ws -> Weight assigned to the ontology specialization criterion.
        ---
        ontology_list -> If you want knitLifeSciencie to USE a specific ontology, you must put the acronym here
        ontology_denied -> If you want knitLifeSciencie NOT TO USE any ontology, you must put the acronym here

        Example to use: 
            wc = 0.8
            wa = 0.8
            wd = 0.8
            ws = 0.8
            ontlology_list = NCIT,MESH,CODO
            ontology_denied = NCIT,MESH,CODO
            