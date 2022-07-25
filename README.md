# KNIT

The KNIT algorithm creates a workflow that aims to detect the existing knowledge of a specific domain, collect the most relevant ontologies, study their interconnection and display the result as a new ontology adjusted to the research needs.

With this idea, the KnitBio tool is developed.

![KNITBIO](docs/source/knitbio.svg)

KnitBio is a powerful tool designed to streamline the process of creating ontologies in LifeScience domains using the KNIT algorithm. To do this, it uses ontologies already made in the Bioportal, AgroPortal, EcoPortal or MedPortal.
To perform this function, we must provide the tools with the main terms we want to study in our future ontology. With this data (along with other parameters specified in the operation section), KnitBio reviews the chosen database (BioPortal, AgroPortal, EcoPortal, MedPortal), selecting the most accurate ontologies for the input terms.
This ontology can be studied in OWL format or visually in the Neo4j database.

## Requirements
