import __init__
import pandas as pd
from decouple import config
from knitbio.first_layer import knit

print(config("API_KEY"))


def star_knit(
    sparql_service,
    REST_URL: str,
    path_csv_file: str,
    sep_csv: str,
    wc: str,
    wa: str,
    wd: str,
    ws: str,
    ontology_list: list,
    ontology_denied: list,
):

    df = pd.read_csv(path_csv_file, sep=sep_csv, dtype="str")
    list_text = []
    for row in df:
        list_text.append(row.upper().replace('"', ""))

    while len(list_text) >= 100:

        knit(
            sparql_service,
            REST_URL,
            list_text[0:100],
            (config("API_KEY")),
            (config("IP_SERVER_NEO4J")),
            (config("USER_NEO4J")),
            (config("PASSWORD_NEO4J")),
            wc,
            wa,
            wd,
            ws,
            ontology_list,
            ontology_denied,
        )
        for element in list_text[0:100]:
            list_text.remove(element)
    else:

        knit(
            sparql_service,
            REST_URL,
            list_text,
            (config("API_KEY")),
            (config("IP_SERVER_NEO4J")),
            (config("USER_NEO4J")),
            (config("PASSWORD_NEO4J")),
            wc,
            wa,
            wd,
            ws,
            ontology_list,
            ontology_denied,
        )


star_knit(
    (config("sparql_service")),
    (config("REST_URL")),
    (config("path_csv")),
    (config("sep_csv")),
    (config("wc")),
    (config("wa")),
    (config("wd")),
    (config("ws")),
    (config("ontology_list")),
    (config("ontology_denied")),
)

print("end_!")


