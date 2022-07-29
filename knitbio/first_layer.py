import json
import requests
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from tqdm import tqdm

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
        ontology_denied=list
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

    query_neo4j_str(IP_SERVER_NEO4J,
                    USER_NEO4J,
                    PASSWORD_NEO4J,
                    ("MATCH (n) detach delete n"), )

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

    def reverse_url_encoding(text: str):  

        dicc_replace = {":": "%3A", "/": "%2F", "#": "%23"}
        for x, y in dicc_replace.items():
            text = text.replace(x, y)
        return text

    def knit_data(uri: str, acronym: str):

        """ 

        :param uri: 
        :param acronym:
        """

        url_uri = reverse_url_encoding(uri)
        print(REST_URL + "/ontologies/" + acronym + "/classes/" + url_uri + "/?apikey=" + API_KEY)
        


    def recommend_bioportal(list_label: list, ontology_denied: list, wc: str, wa: str, wd: str, ws: str,
                            ONTOLOGY: list):

        """
        :param list_label: 
        :param ontology_denied:

        """

        spider = {}
        head_str = ",".join(list_label)
        head_str_replace = head_str.replace(
            "_", " "
        )  

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

    

    recommend_bioportal(list_text, ontology_denied, wc, wa, wd, ws, ONTOLOGY)
