from decouple import config
import rdflib
from neo4j import GraphDatabase
from rdflib import Graph
from rdflib.namespace import RDFS, RDF, OWL, XSD
from tqdm import tqdm
from knitbio.py_query_cypher import query_neo4j_list


def neo2RDF(IP_SERVER_NEO4J,USER_NEO4J,PASSWORD_NEO4J, API_KEY, sparql_service):

    all_class_uri = [element["n"] for element in
            query_neo4j_list(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, ("MATCH(n:Class) RETURN n"))]
    all_property_uri = [element["n"] for element in
            query_neo4j_list(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, ("MATCH(n:Propety) RETURN n"))]
    all_type_elem = [element for element in
            query_neo4j_list(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, ("MATCH(a)-[b]->(c) RETURN a.uri,b.uri,c.uri,b.type"))]

    g = Graph()
    list_elemnt_with_label = []
    element_no_class = []
    graph_object_prop = {}
    list_object_prop = []
    list_other_prop= []
    list_type_element_class = []
    list_type_element_individual = []
    list_type_element_objectProperty = []
    list_type_element_restriction = []

    for element_type in all_type_elem:
        if element_type['c.uri'] == 'http://www.w3.org/2002/07/owl#NamedIndividual':
            list_type_element_individual.append(element_type['a.uri'])
        if element_type['c.uri'] == 'http://www.w3.org/2002/07/owl#Class':
            list_type_element_class.append(element_type['a.uri'])
        if element_type['b.type'] == "http://www.w3.org/2002/07/owl#ObjectProperty":
            list_type_element_objectProperty.append(element_type['b.uri'])


    """
    Basic notations of definition: synonyms and acronyms of ontologies.
    """

    URI_definition ='http://ontologies.khaos.uma.es/comment#definition'
    URI_synonym = 'http://ontologies.khaos.uma.es/comment#synonym'
    URI_ontology = 'http://ontologies.khaos.uma.es/comment#ontology_acronm'
    g.add((rdflib.URIRef(URI_definition), RDF.type, OWL.AnnotationProperty))
    g.add((rdflib.URIRef(URI_definition), RDFS.subPropertyOf, RDFS.comment))
    g.add((rdflib.URIRef(URI_synonym), RDF.type, OWL.AnnotationProperty))
    g.add((rdflib.URIRef(URI_synonym), RDFS.subPropertyOf, RDFS.comment))
    g.add((rdflib.URIRef(URI_ontology), RDF.type, OWL.AnnotationProperty))
    g.add((rdflib.URIRef(URI_ontology), RDFS.subPropertyOf, RDFS.comment))

    for elemnt_class in tqdm(all_class_uri):

        """
        This function creates classes, as long as the "class" is not 'Thing'.
        Depending on whether b.type and b.label are different from "None", they must be described differently.       
        """

        print(elemnt_class)
