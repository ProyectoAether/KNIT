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

        sleep = 60

        while True:
            try:
                url_self = requests.get(
                    REST_URL + "/ontologies/" + onto + "/classes/" + uri_1,
                    headers=headers,
                )
                break
            except:
                time.sleep(sleep)
                sleep += 60

        status = str(url_self.status_code)
        list_mapp = []
        if status == "200":
            url_self_1 = json.loads(url_self.content)
            url_parents = url_self_1["links"]["parents"] + "/?apikey=" + API_KEY
            url_mapping = url_self_1["links"]["mappings"] + "/?apikey=" + API_KEY
            sleep = 60
            while True:
                try:
                    url_parents_1 = requests.get(url_parents)
                    break
                except:
                    time.sleep(sleep)
                    sleep += 60

            url_parents_2 = json.loads(url_parents_1.content)
            sleep = 60

            while True:
                try:
                    url_mapping_1 = requests.get(url_mapping)
                    break
                except:
                    time.sleep(sleep)
                    sleep += 60

            url_mapping_2 = json.loads(url_mapping_1.content)
            for element in url_mapping_2:
                classes = element["classes"]
                id = classes[1]["@id"]
                list_mapp.append(id)
            all_uri_neo4j = [
                uri["n.uri"]
                for uri in query_neo4j_list(
                    IP_SERVER_NEO4J,
                    USER_NEO4J,
                    PASSWORD_NEO4J,
                    ("MATCH(n:Class) RETURN n.uri"),
                )
            ]
            for id in list_mapp:
                if id in all_uri_neo4j and uri != id:
                    """
                    algunos elemento poesen entres sus mappings asi mismos, para evitar que se generen estos enlaces recursivos uri!=id
                    """
                    query_neo4j_str(
                        IP_SERVER_NEO4J,
                        USER_NEO4J,
                        PASSWORD_NEO4J,
                        (
                            f"""
                        MATCH (a {{uri: "{uri}"}}),(b {{uri:"{id}"}})
                        MERGE (a)-[:mapping {{uri:'http://www.w3.org/2002/07/owl#equivalentClass'}}]->(b)-[:mapping {{uri:'http://www.w3.org/2002/07/owl#equivalentClass'}}]->(a)
                        """
                        ),
                    )
            all_mapping_neo4j = [
                uri["n.uri"]
                for uri in query_neo4j_list(
                    IP_SERVER_NEO4J,
                    USER_NEO4J,
                    PASSWORD_NEO4J,
                    ("MATCH (n:Class)-[:mapping]->() RETURN n.uri"),
                )
            ]
            if len(url_parents_2) == 0:
                parent_exit = f"""
                            MATCH (a {{uri: "{uri}"}}),(b {{uri:'http://www.w3.org/2002/07/owl#Thing'}})
                            MERGE (a)-[:SCO {{uri: 'http://www.w3.org/2000/01/rdf-schema#subClassOf'}}]->(b)
                            """
                query_neo4j_str(
                    IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, parent_exit
                )
            else:
                for data in url_parents_2:
                    uri_parent = data["@id"]
                    if not uri in all_mapping_neo4j:
                        """
                        si uri esta posee un mapping es como si el elemnto en cuestion ya exitiese, por ello tomamos la rama a la que se adiere como buen y dejamos de tejer"
                        """
                        data_elemet(data, onto)
                        mapping_parent = f"""
                                    MATCH (a {{uri: "{uri}"}}),(b {{uri:"{uri_parent}"}})
                                    MERGE (a)-[:SCO {{uri: 'http://www.w3.org/2000/01/rdf-schema#subClassOf'}}]->(b)
                                    """
                        query_neo4j_str(
                            IP_SERVER_NEO4J,
                            USER_NEO4J,
                            PASSWORD_NEO4J,
                            (mapping_parent),
                        )
                        if not uri_parent in all_uri_neo4j:
                            parents(onto, uri_parent)

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
                        uri_id_class = reverse_url_encoding(id_class)
                        sleep = 60

                        while True:
                            try:
                                url_self_pro = requests.get(
                                    REST_URL
                                    + "/ontologies/"
                                    + acronym
                                    + "/classes/"
                                    + uri_id_class,
                                    headers=headers,
                                )
                                break
                            except:
                                time.sleep(sleep)
                                sleep += 60

                        status = str(url_self_pro.status_code)
                        if status == "200":
                            url_self_1 = json.loads(url_self_pro.content)
                            query_neo4j_str(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                (
                                    f"""
                                    MATCH (a {{uri:"{str(url_self_1['@id'])}"}}) SET a:Column
                                    """
                                ),
                            )
                            query_neo4j_str(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                (
                                    f"""
                                    MATCH (a {{uri:"{str(url_self_1['@id'])}"}}) SET a.name_Dataset ="{label_class}"
                                    """
                                ),
                            )
                        else:
                            new_index.remove(
                                label_class
                            )  # TODO:  search !!!!

                new_list = head_str.split(",")
                for a in new_index:
                    """
                    para encontrar los nodos que no han sido dibujados 
                    """
                    if a in new_list:
                        new_list.remove(a)
                    else:
                        node_clear = a.replace(" ", "_")
                        new_list.remove(
                            node_clear
                        )  

                list_label = new_list

            else:
                print("\n\nthere is no ontological recommendation for any of the provided classes\n\n")

            list_label_denied = []
            if len(list_label) > 1:
                for element_not_found in list_label:
                    print(element_not_found)
                    list_label_denied.append(element_not_found)
                    if len(denied) == 0:
                        for label in list_label:
                            query_neo4j_str(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                (
                                    f"""
                                            MERGE (a:Class {{label:"{label.lower()}",name:"{label.lower()}", uri:"http://ontologies.khaos.uma.es#{(label.lower()).replace(' ', '_')}", name_Dataset:"{label}", definition:"{label}", synonym:"{label}"}}) SET a:Column
                                            """
                                ),
                            )
                            query_neo4j_str(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                (
                                    f"""
                                            MATCH (a {{uri:"http://ontologies.khaos.uma.es#{(label.lower()).replace(' ', '_')}"}}),(b {{uri:'http://www.w3.org/2002/07/owl#Thing'}})
                                            MERGE (a)-[:SCO {{uri: 'http://www.w3.org/2000/01/rdf-schema#subClassOf'}}]->(b)
                                            """
                                ),
                            )
                            query_neo4j_str(
                                IP_SERVER_NEO4J,
                                USER_NEO4J,
                                PASSWORD_NEO4J,
                                (
                                    f"""
                                            MATCH (a {{uri: "{label.lower()}"}}),(b {{uri:"http://www.w3.org/2002/07/owl#Class"}}) MERGE(a)-[:PROPERTY {{uri:"http://www.w3.org/1999/02/22-rdf-syntax-ns#type"}}]->(b)
                                            """
                                ),
                            )

                        for label in list_label:
                            list_all_label_neo4j = [
                                str(uri["n.name"]).lower()
                                for uri in query_neo4j_list(
                                    IP_SERVER_NEO4J,
                                    USER_NEO4J,
                                    PASSWORD_NEO4J,
                                    ("MATCH(n:Class) RETURN n.name"),
                                )
                            ]
                            if label.lower() not in list_all_label_neo4j:
                                query_neo4j_str(
                                    IP_SERVER_NEO4J,
                                    USER_NEO4J,
                                    PASSWORD_NEO4J,
                                    (
                                        f"""
                                            MERGE (a:Class {{name:"{label.lower()}", uri:"{label.lower()}", name_Dataset: "{label}"}}) SET a:Column 
                                            """
                                    ),
                                )
                                query_neo4j_str(
                                    IP_SERVER_NEO4J,
                                    USER_NEO4J,
                                    PASSWORD_NEO4J,
                                    (
                                        f"""
                                            MATCH (a {{uri: "{label.lower()}"}}),(b {{uri:'http://www.w3.org/2002/07/owl#Thing'}})
                                            MERGE (a)-[:SCO {{uri: 'http://www.w3.org/2000/01/rdf-schema#subClassOf'}}]->(b)
                                            """
                                    ),
                                )
                    else:
                        denied.clear()
                        recommend_bioportal(list_label, set(list_acronym_denied), wa, wd, ws)

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

        def property_class(uri_sparql: str, sparql_service: str, API_KEY: str, all_class: list, all_property: list,
                       list_uri: list, ontology: str, IP_SERVER_NEO4J: str, USER_NEO4J: str, PASSWORD_NEO4J: str):
            type_elemnt_class = 'http://www.w3.org/2002/07/owl#Class'
            sparql = SPARQLWrapper(sparql_service)
            if sparql_service == 'http://sparql.bioontology.org/sparql/':
                sparql.addCustomParameter("apikey", API_KEY)

            query_sparql = f"""
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                        SELECT DISTINCT  ?elementB  ?property  ?type_elementB ?label_elementB ?label_property ?type_prop
                        WHERE {{ 
                            ?elementB  ?property <{uri_sparql}>.
                            ?elementB rdf:type ?type_elementB.
                            Optional{{?property rdf:type  ?type_prop}}.
                            Optional{{?property rdfs:label ?label_property}}.
                            Optional{{?elementB rdfs:label ?label_elementB}}.
                            }}"""
            # TODO: for variables whith get, you do whitout optional
            sparql.setQuery(query_sparql)
            sparql.setReturnFormat(JSON)
            if sparql_service != 'http://sparql.bioontology.org/sparql/':
                sparql.setMethod(GET)

            try:
                if len(sparql.query().convert()["results"]["bindings"]) > 0:
                    for response in sparql.query().convert()["results"]["bindings"]:
                        if response['property']['value'] != 'http://www.w3.org/2000/01/rdf-schema#subClassOf' and \
                                response['property']['value'] != 'http://www.w3.org/2002/07/owl#disjointWith':

                            # if response['type_elementB']['value'] == 'http://www.w3.org/2002/07/owl#Class' and  response['type_prop']['value'] != 'http://www.w3.org/2002/07/owl#AnnotationProperty':
                            if response['type_elementB']['value'] == 'http://www.w3.org/2002/07/owl#Class':
                                if response['elementB']['value'] not in all_class and response['elementB'][
                                    'value'] not in list_uri:
                                    list_uri.append(response['elementB'][
                                                        'value'])  ######## TODO:  peta with st list index out of range !!!!
                                    try:
                                        """need to know the acronym of the ontology to which it belongs
                                        
                                        PREFIX omv: <http://omv.ontoware.org/2005/05/ontology#>
                                        SELECT  DISTINCT ?acr
                                        WHERE  { GRAPH ?grah {<http://purl.obolibrary.org/obo/TRAK_0000086> ?p ?o}.
                                                ?ont ?r ?grah.
                                                ?ont omv:acronym ?acr
                                                } 
                                        """
                                        sparql_acron = SPARQLWrapper(sparql_service)
                                        if sparql_service == 'http://sparql.bioontology.org/sparql/':
                                            sparql_acron.addCustomParameter("apikey", API_KEY)

                                        query_acron = f"""
                                                        PREFIX omv: <http://omv.ontoware.org/2005/05/ontology#>
                                                        SELECT  DISTINCT ?acr
                                                        WHERE  {{ GRAPH ?grah {{<{response['elementB']['value']}> ?p ?o}}.
                                                                ?ont ?r ?grah.
                                                                ?ont omv:acronym ?acr
                                                                }}
                                                    """

                                        sparql_acron.setQuery(query_acron)
                                        sparql_acron.setReturnFormat(JSON)
                                        if sparql_service != 'http://sparql.bioontology.org/sparql/':
                                            sparql.setMethod(GET)

                                        if (len(sparql_acron.query().convert()["results"]["bindings"])) > 0:
                                            knit_data(response['elementB']['value'], (
                                            sparql_acron.query().convert()["results"]["bindings"][-1]["acr"][
                                                "value"]).upper())
                                                """
                                                    at this point it is important to give a type to the new elements that have been created, which is why it is proposed that that as it cannot be a child class of anything but other classes (subclasses) the new elements must be classes. Therefore, we make a new call, and to retrieve a list of all our elements at the current time and from this list we remove the previous elements and the list_uri. These results are traversed with a for and are given the type of classes at the same time they are integrated into list_uri for similar results.                                           
                                                """
                                            current_list_uri = [(uri["n.uri"]) for uri in query_neo4j_list(
                                                IP_SERVER_NEO4J,
                                                USER_NEO4J,
                                                PASSWORD_NEO4J,
                                                ("MATCH(n:Class) RETURN n.uri"), )]
                                            for new_uri in list_uri:
                                                all_class.append(new_uri)

                                            for old_uri in all_class:
                                                if old_uri in current_list_uri:
                                                    current_list_uri.remove(old_uri)

                                            for news_uri_neo in current_list_uri:
                                                query_type_new_uri = f"""MATCH (a {{uri:"{news_uri_neo}"}}),(b {{uri:'{type_elemnt_class}'}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b)"""
                                                query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J,
                                                                (query_type_new_uri))
                                    except:
                                        # TODO:"If the process of creating fails, it has to be constructed in an artificial way (not included in the api"
                                        if (len(sparql_acron.query().convert()["results"]["bindings"])) > 0:
                                            acrom_elem = (
                                            sparql_acron.query().convert()["results"]["bindings"][-1]["acr"]["value"])
                                        else:
                                            acrom_elem = "unknown"
                                        query_neo4j_str(
                                            IP_SERVER_NEO4J,
                                            USER_NEO4J,
                                            PASSWORD_NEO4J,
                                            ("MERGE (a:Class {name:'" + str(
                                                response['elementB']['value']) + "', label:'" + str(
                                                response['elementB']['value']) + "', uri:'" + str(response['elementB'][
                                                                                                    'value']) + "', synonym:'', definition:'', ontology:'" + acrom_elem + "'})"),
                                        )
                                query_type_elemnt = f"""MATCH (a {{uri:"{response['elementB']['value']}"}}),(b {{uri:"http://www.w3.org/2002/07/owl#Class"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b)"""
                                query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_type_elemnt))
                                if len(response.get('type_prop')) >= 1 and len(response.get('label_property')) >= 1:
                                    query_element = f"""MATCH (a {{uri:"{response['elementB']['value']}"}}),(b {{uri:"{uri_sparql}"}}) MERGE (a)-[:PROPERTY {{uri:'{response['property']['value']}', label: '{response['label_property']['value']}', type: '{response['type_prop']['value']}'}}]->(b)"""
                                else:
                                    query_element = f"""MATCH (a {{uri:"{response['elementB']['value']}"}}),(b {{uri:"{uri_sparql}"}}) MERGE (a)-[:PROPERTY {{uri:'{response['property']['value']}'}}]->(b)"""

                                query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_element))

                            if response['type_elementB']['value'] != 'http://www.w3.org/2002/07/owl#Class' and len(response.get('label_elementB')) >= 1:
                                #TODO: the above if it is possible to mention the existence of label,
                                #TODO: len(response.get('label_elementB')) >= 1
                                if response['elementB']['value'] not in all_property and response['elementB'][
                                    'value'] not in list_uri:
                                    list_uri.append(response['elementB']['value'])
                                    query_new_propety = f"""MERGE (a:Propety {{uri:"{response['elementB']['value']}", label:"{response['label_elementB']['value']}"}})"""
                                    query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_new_propety))

                                    # TODO: in the next else enter the restinations and somevalue, very interesting at the level of reasoner.
                                    #if len(response.get('label_elementB')) >= 1:
                                    #   query_new_propety = f"""MERGE (a:Propety {{uri:"{response['elementB']['value']}", label:"{response['label_elementB']['value']}"}})"""
                                    #   query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_new_propety))
                                    #else:
                                    #    query_new_propety = f"""MERGE (a:Propety {{uri:"{response['elementB']['value']}", label:"{response['elementB']['value']}"}})"""
                                    #    query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_new_propety))
                                if response['type_elementB']['value'] not in all_class and response['type_elementB'][
                                    'value'] not in list_uri:
                                    list_uri.append(response['type_elementB']['value'])
                                    query_type_property = f""" MERGE (a:Class {{uri:"{response['type_elementB']['value']}"}})"""
                                    query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_type_property))

                                query_element = f"""MATCH (a {{uri:"{response['elementB']['value']}"}}),(b {{uri:"{uri_sparql}"}}) MERGE (a)-[:PROPERTY {{uri:'{response['property']['value']}'}}]->(b)"""
                                query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_element))

                                query_type = f"""MATCH (a {{uri:"{response['elementB']['value']}"}}),(b {{uri:"{response['type_elementB']['value']}"}}) MERGE (a)-[:PROPERTY {{uri:'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'}}]->(b)"""
                                query_neo4j_str(IP_SERVER_NEO4J, USER_NEO4J, PASSWORD_NEO4J, (query_type))


            except Exception as e:
                print(e)