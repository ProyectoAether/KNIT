import json
import requests
import time
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from tqdm import tqdm
from knitbio.py_query_cypher import query_neo4j_list, query_neo4j_str

denied = 0
List_node_news = []


def knit(
    sparql_service: str,
    REST_URL: str,
    list_text: list,
    API_KEY: str,
    IP_SERVER_NEO4J: str,
    USER_NEO4J: str,
    PASSWORD_NEO4J: str,
    wc: str,
    wa: str,
    wd: str,
    ws: str,
    ONTOLOGY: list,
    ontology_denied=list,
):
    """
    :param list_text:
    :param API_KEY
    :param IP_SERVER_NEO4j
    :param USER_NEO4J:
    :param PASSWORD_NEO4j:
    """

    headers = {"Authorization": "apikey token=" + API_KEY}

    list_seach_cero = []
    list_acronym_denied = ontology_denied
    denied = []

    query_neo4j_str(
        IP_SERVER_NEO4J,
        USER_NEO4J,
        PASSWORD_NEO4J,
        ("MATCH (n) detach delete n"),
    )

    query_neo4j_str(
        IP_SERVER_NEO4J,
        USER_NEO4J,
        PASSWORD_NEO4J,
        (
            f"""
            MERGE (a:Class {{name:'THING', label:'THING', uri:'http://www.w3.org/2002/07/owl#Thing'}}) SET a:THING
            """
        ),
    )

    def knit_data(uri: str, acronym: str):

        url_uri = reverse_url_encoding(uri)
        print(
            REST_URL
            + "/ontologies/"
            + acronym
            + "/classes/"
            + url_uri
            + "/?apikey="
            + API_KEY
        )
        while True:
            try:

                url_self = requests.get(
                    REST_URL + "/ontologies/" + acronym + "/classes/" + url_uri,
                    headers=headers,
                )
                break
            except:
                time.sleep(sleep)
                sleep += 60
        status = str(url_self.status_code)
        if status == "200":
            url_self_1 = json.loads(url_self.content)
            data_elemet(url_self_1, acronym)
            parents(acronym, uri)

        if status != "200":
            list_acronym_denied.append(acronym)
            denied.append(acronym)

    def parents(onto: str, uri: str):
        uri_1 = reverse_url_encoding(uri)

    def recommend_bioportal(
        list_label: list,
        ontology_denied: list,
        wc: str,
        wa: str,
        wd: str,
        ws: str,
        ONTOLOGY: list,
    ):

        """
        :param list_label=
        :param ontology_denied=
        """
        spider = {}
        head_str = ",".join(list_label)
        head_str_replace = head_str.replace("_", " ")

        sleep = 60
        while True:
            try:
                if len(ONTOLOGY) >= 1:
                    recommend = requests.get(
                        REST_URL
                        + "/recommender?input="
                        + head_str_replace
                        + "&input_type=2&wc="
                        + wc
                        + "&wa="
                        + wa
                        + "&wd="
                        + wd
                        + "&ws="
                        + ws
                        + "&ontologies="
                        + ONTOLOGY,
                        headers=headers,
                    )

                else:
                    recommend = requests.get(
                        REST_URL
                        + "/recommender?input="
                        + head_str_replace
                        + "&input_type=2&wc="
                        + wc
                        + "&wa="
                        + wa
                        + "&wd="
                        + wd
                        + "&ws="
                        + ws,
                        headers=headers,
                    )
                break
            except:
                time.sleep(sleep)
                sleep += 60

        recommend_json = json.loads(recommend.content)
        try:
            if len(recommend_json) >= 1:
                new_index = []
                for ontology in recommend_json:
                    for data in ontology["ontologies"]:
                        acronym = data["acronym"]
                    for data_2 in ontology["coverageResult"]["annotations"]:
                        label_class = data_2["text"]
                        id_class = data_2["annotatedClass"]["@id"]
                        if not label_class in spider and acronym not in ontology_denied:
                            spider.update({label_class: {id_class: acronym}})
                for label_class, id_class_acronym in tqdm(spider.items()):
                    new_index.append(label_class)
                    for id_class, acronym in id_class_acronym.items():
                        list_seach_cero.append(acronym)
                        knit_data(id_class, acronym)

        except Exception as e:
            print(e)

    def reverse_url_encoding(text: str):
        dicc_replace = {":": "%3A", "/": "%2F", "#": "%23"}
        for x, y in dicc_replace.items():
            text = text.replace(x, y)
        return text

    recommend_bioportal(list_text, ontology_denied, wc, wa, wd, ws, ONTOLOGY)

    def property_sparql(uri_sparql: str, ontology: str):
        """
        :uri_sparql=
        :ontology=
        """
        list_uri = []
        sparql = SPARQLWrapper(sparql_service)
        if sparql_service == "http://sparql.bioontology.org/sparql/":
            sparql.addCustomParameter("apikey", API_KEY)

        if uri_sparql != "http://www.w3.org/2002/07/owl#Thing":
            all_class = [
                (uri["n.uri"])
                for uri in query_neo4j_list(
                    IP_SERVER_NEO4J,
                    USER_NEO4J,
                    PASSWORD_NEO4J,
                    ("MATCH(n:Class) RETURN n.uri"),
                )
            ]
            all_property = [
                (uri["n.uri"])
                for uri in query_neo4j_list(
                    IP_SERVER_NEO4J,
                    USER_NEO4J,
                    PASSWORD_NEO4J,
                    ("MATCH(n:Property) RETURN n.uri"),
                )
            ]
            query_sparql = f"""
                                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                    SELECT DISTINCT *
                                    WHERE {{ 
                                    <{uri_sparql}> rdf:type ?elementB.
                                    }}
                                    """
            sparql.setQuery(query_sparql)
            sparql.setReturnFormat(JSON)

            if sparql_service != "http://sparql.bioontology.org/sparql/":
                sparql.setMethod(GET)

            list_type_elemnt = []
            try:
                if len(sparql.query().convert()["results"]["bindings"]) < 1:
                    list_type_elemnt.append("http://www.w3.org/2002/07/owl#Class")
                    type_elemnt = "http://www.w3.org/2002/07/owl#Class"
                    if type_elemnt not in all_class and type_elemnt not in list_uri:
                        query_type = f"""MATCH (a {{uri:"{uri_sparql}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b:Class {{uri:"{type_elemnt}"}})"""
                        list_uri.append(type_elemnt)
                    else:
                        query_type = f"""MATCH (a {{uri:"{uri_sparql}"}}),(b {{uri:"{type_elemnt}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b)"""
                    query_neo4j_str(
                        IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_type)
                    )

                # It is necessary to know the type to understand how to perform the following query

                else:
                    for response in sparql.query().convert()["results"]["bindings"]:
                        list_type_elemnt.append(response["elementB"]["value"])
                        type_elemnt = response["elementB"]["value"]

                        if type_elemnt not in all_class and type_elemnt not in list_uri:
                            query_type = f"""MATCH (a {{uri:"{uri_sparql}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b:Class {{uri:"{type_elemnt}"}})"""
                            list_uri.append(type_elemnt)

                        else:
                            query_type = f"""MATCH (a {{uri:"{uri_sparql}"}}),(b {{uri:"{type_elemnt}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b)"""
                        query_neo4j_str(
                            IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_type)
                        )

            except Exception as e:
                print(e)
                list_type_elemnt.append("http://www.w3.org/2002/07/owl#Class")

            if "http://www.w3.org/2002/07/owl#Class" in list_type_elemnt:
                property_class(
                    uri_sparql,
                    sparql_service,
                    API_KEY,
                    all_class,
                    all_property,
                    list_uri,
                    ontology,
                    IP_SERVER_NEO4J,
                    USER_NEO4J,
                    PASSWORD_NEO4J,
                )

            else:
                for uri_type in list_type_elemnt:
                    query_sparql = f"""
                                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                        SELECT DISTINCT *
                                        WHERE {{ 
                                        <{uri_type}> rdf:type ?elementB.
                                        }}
                                            """

                    sparql.setQuery(query_sparql)
                    sparql.setReturnFormat(JSON)
                    if sparql_service != "http://sparql.bioontology.org/sparql/":
                        sparql.setMethod(GET)

                    try:
                        if len(sparql.query().convert()["results"]["bindings"]) > 0:
                            for response in sparql.query().convert()["results"][
                                "bindings"
                            ]:
                                if (
                                    response["elementB"]["value"]
                                    == "http://www.w3.org/2002/07/owl#Class"
                                ):
                                    type_elemnt = "http://www.w3.org/2002/07/owl#Class"
                                    if (
                                        type_elemnt not in all_class
                                        and type_elemnt not in list_uri
                                    ):
                                        query_type = f"""MATCH (a {{uri:"{uri_type}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b:Class {{uri:"{type_elemnt}"}})"""
                                        list_uri.append(type_elemnt)
                                    else:
                                        query_type = f"""MATCH (a {{uri:"{uri_type}"}}),(b {{uri:"{type_elemnt}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b)"""
                                    query_neo4j_str(
                                        IP_SERVER_NEO4J,
                                        USER_NEO4J,
                                        PASSWORD_NEO4J,
                                        (query_type),
                                    )
                                    property_class(
                                        uri_type,
                                        sparql_service,
                                        API_KEY,
                                        all_class,
                                        all_property,
                                        list_uri,
                                        ontology,
                                        IP_SERVER_NEO4J,
                                        USER_NEO4J,
                                        PASSWORD_NEO4J,
                                    )

                    except Exception as e:
                        print(e)

            if sparql_service == "http://sparql.bioontology.org/sparql/":
                sparql.addCustomParameter("apikey", API_KEY)

            data_query = f"""   PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                                SELECT DISTINCT ?b ?c ?e
                                WHERE {{
                                <{uri_sparql}> ?b ?c.
                                ?b rdf:type owl:DatatypeProperty.
                                ?b rdfs:label ?e.
                                }}"""

            disjointWith_query = f"""
                                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                                SELECT DISTINCT ?b ?c ?e
                                WHERE {{
                                <{uri_sparql}> owl:disjointWith ?b.
                                ?b rdfs:label ?e.
                                }}"""

            sparql.setQuery(data_query)
            sparql.setReturnFormat(JSON)
            if sparql_service != "http://sparql.bioontology.org/sparql/":
                sparql.setMethod(GET)

            try:
                for response in sparql.query().convert()["results"]["bindings"]:
                    if (
                        "http://www.w3.org/2002/07/owl#NamedIndividual"
                        in list_type_elemnt
                    ):
                        query_data_property = f""" MATCH (a {{uri:'{uri_sparql}'}}) MERGE (a)-[:PROPERTY {{ uri:'{response['b']['value']}', label:'{response['e']['value']}', type:'http://www.w3.org/2002/07/owl#DatatypeProperty'}}]->(b:Literal {{data:"{(response['c']['value']).replace('"', "'")}"}})
                        """
                    if "http://www.w3.org/2002/07/owl#Class" in list_type_elemnt:
                        query_data_property = f""" MATCH (a {{uri:'{uri_sparql}'}}) MERGE (a)-[:PROPERTY {{ uri:'{response['b']['value']}', label:'{response['e']['value']}', type:'http://www.w3.org/2002/07/owl#AnnotationProperty'}}]->(b:Literal {{data:"{(response['c']['value']).replace('"', "'")}"}})
                        """
                    query_neo4j_str(
                        IP_SERVER_NEO4J,
                        USER_NEO4J,
                        PASSWORD_NEO4J,
                        (query_data_property),
                    )
            except Exception as e:
                print(e)

            sparql.setQuery(disjointWith_query)
            sparql.setReturnFormat(JSON)
            if sparql_service != "http://sparql.bioontology.org/sparql/":
                sparql.setMethod(GET)
            try:
                for response in sparql.query().convert()["results"]["bindings"]:
                    try:
                        knit_data(response["b"]["value"], ontology)
                    except:
                        exit_disjoint = query_neo4j_list(
                            IP_SERVER_NEO4J,
                            USER_NEO4J,
                            PASSWORD_NEO4J,
                            (
                                f"""MATCH(n {{uri:'{response['b']['value']}'}}) RETURN n.uri"""
                            ),
                        )
                        if exit_disjoint == []:
                            query_new_class_disjoint = f""" MERGE (a:Class {{uri:'{response['b']['value']}', label:'{response['e']['value']}'}})
                            """
                            query_neo4j_str(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                (query_new_class_disjoint),
                            )

                    query_neo_disjoint = f"""
                        MATCH (a {{uri:'{uri_sparql}'}}),(b {{uri:'{response['b']['value']}'}}) MERGE (a)-[:PROPERTY {{ uri:'http://www.w3.org/2002/07/owl#disjointWith'}}]->(b)
                    """
                    query_neo4j_str(
                        IP_SERVER_NEO4J,
                        USER_NEO4J,
                        PASSWORD_NEO4J,
                        (query_neo_disjoint),
                    )

            except Exception as e:
                print(e)
