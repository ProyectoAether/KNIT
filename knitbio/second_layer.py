from decouple import config
import rdflib
from neo4j import GraphDatabase
from rdflib import Graph
from rdflib.namespace import RDFS, RDF, OWL, XSD
from tqdm import tqdm
from knitbio.py_query_cypher import query_neo4j_list


def neo2RDF(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, API_KEY, sparql_service):

    all_class_uri = [
        element["n"]
        for element in query_neo4j_list(
            IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, ("MATCH(n:Class) RETURN n")
        )
    ]
    all_property_uri = [
        element["n"]
        for element in query_neo4j_list(
            IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, ("MATCH(n:Propety) RETURN n")
        )
    ]
    all_type_elem = [
        element
        for element in query_neo4j_list(
            IP_SERVER_NEO4J,
            USER_NEO4J,
            PASSWORD_NEO4J,
            ("MATCH(a)-[b]->(c) RETURN a.uri,b.uri,c.uri,b.type"),
        )
    ]

    g = Graph()
    list_elemnt_with_label = []
    element_no_class = []
    graph_object_prop = {}
    list_object_prop = []
    list_other_prop = []
    list_type_element_class = []
    list_type_element_individual = []
    list_type_element_objectProperty = []
    list_type_element_restriction = []

    for element_type in all_type_elem:
        if element_type["c.uri"] == "http://www.w3.org/2002/07/owl#NamedIndividual":
            list_type_element_individual.append(element_type["a.uri"])
        if element_type["c.uri"] == "http://www.w3.org/2002/07/owl#Class":
            list_type_element_class.append(element_type["a.uri"])
        if element_type["b.type"] == "http://www.w3.org/2002/07/owl#ObjectProperty":
            list_type_element_objectProperty.append(element_type["b.uri"])

    """
    Basic notations of definition: synonyms and acronyms of ontologies.
    """

    URI_definition = "http://ontologies.khaos.uma.es/comment#definition"
    URI_synonym = "http://ontologies.khaos.uma.es/comment#synonym"
    URI_ontology = "http://ontologies.khaos.uma.es/comment#ontology_acronm"
    g.add((rdflib.URIRef(URI_definition), RDF.type, OWL.AnnotationProperty))
    g.add((rdflib.URIRef(URI_definition), RDFS.subPropertyOf, RDFS.comment))
    g.add((rdflib.URIRef(URI_synonym), RDF.type, OWL.AnnotationProperty))
    g.add((rdflib.URIRef(URI_synonym), RDFS.subPropertyOf, RDFS.comment))
    g.add((rdflib.URIRef(URI_ontology), RDF.type, OWL.AnnotationProperty))
    g.add((rdflib.URIRef(URI_ontology), RDFS.subPropertyOf, RDFS.comment))

    for elemnt_class in tqdm(all_class_uri):

        """
        This function creates classes, as long as the "class" is not 'Thing'.
        Depending on whether b.type and b.label are different from "None",
        they must be described differently.
        """

        consult_query_class = query_neo4j_list(
            IP_SERVER_NEO4J,
            USER_NEO4J,
            PASSWORD_NEO4J,
            (
                'MATCH (a {uri:"'
                + elemnt_class.get("uri")
                + '"})-[b]->(c)  RETURN a, c, b.label,b.uri,b.type'
            ),
        )

        if elemnt_class.get("uri") != "http://www.w3.org/2002/07/owl#Thing":
            for elemnt in consult_query_class:
                """
                As a general rule, in the "BioPortal", and its ecosystem,
                the properties that have the label, and the type, are properties of the ontologies.
                In contrast, properties without these features are generic and widely known.
                """

                if elemnt["b.label"] == None and elemnt["b.type"] == None:
                    if (
                        elemnt["b.uri"]
                        == "http://www.w3.org/2000/01/rdf-schema#subClassOf"
                    ):
                        if (
                            elemnt["a"]["uri"] in list_type_element_individual
                            and elemnt["a"]["uri"] not in list_type_element_class
                        ):
                            uri_1 = elemnt["a"]["uri"]
                            uri_2 = elemnt["c"]["uri"]
                            property_btw_i = property_between_individuals(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                sparql_service,
                                API_KEY,
                                uri_1,
                                uri_2,
                            )
                            if property_btw_i != None:
                                query_replace = f"""MATCH (a {{uri:'{uri_1}'}})-[p {{uri:'http://www.w3.org/2000/01/rdf-schema#subClassOf'}}]->(b {{uri:'{uri_2}'}}) detach delete p"""
                                query_new_prop = f"""MERGE (a {{uri:'{uri_1}'}})-[p {{uri:'{property_btw_i}'}}]->(b {{uri:'{uri_2}'}})"""
                                query_neo4j_list(
                                    IP_SERVER_NEO4J,
                                    USER_NEO4J,
                                    PASSWORD_NEO4J,
                                    (query_replace),
                                )
                                query_neo4j_list(
                                    IP_SERVER_NEO4J,
                                    USER_NEO4J,
                                    PASSWORD_NEO4J,
                                    (query_new_prop),
                                )
                                g.add(
                                    (
                                        rdflib.URIRef(elemnt["a"]["uri"]),
                                        rdflib.URIRef(property_btw_i),
                                        rdflib.URIRef(elemnt["c"]["uri"]),
                                    )
                                )
                            else:
                                query_replace = f"""MATCH (a {{uri:'{uri_1}'}})-[p {{uri:'http://www.w3.org/2000/01/rdf-schema#subClassOf'}}]->(b {{uri:'{uri_2}'}}) detach delete p"""
                                query_neo4j_list(
                                    IP_SERVER_NEO4J,
                                    USER_NEO4J,
                                    PASSWORD_NEO4J,
                                    (query_replace),
                                )
                        else:
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["a"]["uri"]),
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    rdflib.URIRef(elemnt["c"]["uri"]),
                                )
                            )
                    else:
                        g.add(
                            (
                                rdflib.URIRef(elemnt["a"]["uri"]),
                                rdflib.URIRef(elemnt["b.uri"]),
                                rdflib.URIRef(elemnt["c"]["uri"]),
                            )
                        )
                else:
                    if elemnt["c"].get("uri") != None:
                        if (
                            elemnt["b.uri"] in list_type_element_objectProperty
                            and elemnt["a"]["uri"] in list_type_element_class
                        ):
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    RDF.type,
                                    rdflib.URIRef(elemnt["b.type"]),
                                )
                            )
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    RDFS.label,
                                    rdflib.Literal(
                                        elemnt["b.label"], datatype=XSD.string
                                    ),
                                )
                            )
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    rdflib.URIRef(RDFS.domain),
                                    rdflib.URIRef(elemnt["a"]["uri"]),
                                )
                            )
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    rdflib.URIRef(RDFS.range),
                                    rdflib.URIRef(elemnt["c"]["uri"]),
                                )
                            )
                        else:
                            if elemnt["b.type"] != None:
                                g.add(
                                    (
                                        rdflib.URIRef(elemnt["b.uri"]),
                                        RDF.type,
                                        rdflib.URIRef(elemnt["b.type"]),
                                    )
                                )
                            if elemnt["b.label"] != None:
                                g.add(
                                    (
                                        rdflib.URIRef(elemnt["b.uri"]),
                                        RDFS.label,
                                        rdflib.Literal(
                                            elemnt["b.label"], datatype=XSD.string
                                        ),
                                    )
                                )
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["a"]["uri"]),
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    rdflib.URIRef(elemnt["c"]["uri"]),
                                )
                            )
                    else:
                        g.add(
                            (
                                rdflib.URIRef(elemnt["b.uri"]),
                                RDF.type,
                                rdflib.URIRef(elemnt["b.type"]),
                            )
                        )
                        if elemnt["b.label"] != None:
                            g.add(
                                (
                                    rdflib.URIRef(elemnt["b.uri"]),
                                    RDFS.label,
                                    rdflib.Literal(
                                        elemnt["b.label"], datatype=XSD.string
                                    ),
                                )
                            )
                        g.add(
                            (
                                rdflib.URIRef(elemnt["a"]["uri"]),
                                rdflib.URIRef(elemnt["b.uri"]),
                                rdflib.Literal(
                                    elemnt["c"]["data"], datatype=XSD.string
                                ),
                            )
                        )

    for elemnt_propp in tqdm(all_property_uri):

        """
        Similarly, we generate the annotation of properties
        """

        consult_query_prop = query_neo4j_list(
            IP_SERVER_NEO4J,
            USER_NEO4J,
            PASSWORD_NEO4J,
            (
                "MATCH (a {uri:'"
                + elemnt_propp.get("uri")
                + "'})-[b]->(c)  RETURN a.uri, a.label, b.uri, c.uri"
            ),
        )

        for elemnt in consult_query_prop:
            """
            We note the described properties.
            Given that the desired result of this version is the construction of an exemplary and not definitive ontology,
            to avoid complex problems related to null values, we discard data linked to Axioms and restrictions
            (as well as erroneous BioPortal nodes, we suspect that these nodes are previously deleted values)
            """
            if (
                elemnt["c.uri"] != "http://www.w3.org/2002/07/owl#Axiom"
                and elemnt["c.uri"] != "http://www.w3.org/2002/07/owl#Restriction"
            ):
                g.add(
                    (
                        rdflib.URIRef(elemnt["a.uri"]),
                        rdflib.URIRef(elemnt["b.uri"]),
                        rdflib.URIRef(elemnt["c.uri"]),
                    )
                )
                g.add(
                    (
                        rdflib.URIRef(elemnt["a.uri"]),
                        RDFS.label,
                        rdflib.Literal(elemnt["a.label"], datatype=XSD.string),
                    )
                )

    for node_neo in all_class_uri:
        """
        As the last step, the annotations described at the beginning of the script are inserted.
        """

        if node_neo.get("uri") != None:
            label_literal = rdflib.Literal(node_neo.get("label"), datatype=XSD.string)
            g.add((rdflib.URIRef(node_neo.get("uri")), RDFS.label, label_literal))

            dicc_comment = {}
            if node_neo.get("synonym") != None:
                if len((node_neo.get("synonym"))) > 2:
                    term_synonym = rdflib.Literal(
                        node_neo.get("synonym")[1:-1], datatype=XSD.string
                    )
                    g.add(
                        (
                            rdflib.URIRef(node_neo.get("uri")),
                            rdflib.URIRef(URI_synonym),
                            term_synonym,
                        )
                    )
                    # dicc_comment.update({'Synonym': node_neo.get('synonym')[1:-1]})
            if node_neo.get("definition") != None:
                if len((node_neo.get("definition"))) > 2:
                    term_definition = rdflib.Literal(
                        node_neo.get("definition")[1:-1], datatype=XSD.string
                    )
                    g.add(
                        (
                            rdflib.URIRef(node_neo.get("uri")),
                            rdflib.URIRef(URI_definition),
                            term_definition,
                        )
                    )
            if node_neo.get("ontology") != None:
                if len((node_neo.get("ontology"))) >= 1:
                    term_ontology = rdflib.Literal(
                        node_neo.get("ontology"), datatype=XSD.string
                    )
                    g.add(
                        (
                            rdflib.URIRef(node_neo.get("uri")),
                            rdflib.URIRef(URI_ontology),
                            term_ontology,
                        )
                    )
    
    print((g.serialize(format="nt")))

    owl_file = open("output/test_o.owl", "w")
    owl_file.write(g.serialize(format="pretty-xml"))
    owl_file.close()
