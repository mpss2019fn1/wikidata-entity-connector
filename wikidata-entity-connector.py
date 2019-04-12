from argparse import ArgumentParser
from itertools import permutations

import requests
from graphviz import Digraph

wikidata_root_url = "https://www.wikidata.org/"
wikidata_endpoint = "https://query.wikidata.org/sparql"


def process_simple_connection(edges, ent1, ent2):
    query = f"SELECT ?a WHERE {{wd:Q{ent1} ?a wd:Q{ent2}.}}"
    r = requests.get(wikidata_endpoint, params={"format": "json", "query": query})
    for result in r.json()["results"]["bindings"]:
        edges.add((ent1, ent2, result["a"]["value"]))


def process_complex_connection(nodes, edges, ent1, ent3):
    query = f"""
    SELECT ?a ?b ?bLabel ?c WHERE {{
      wd:Q{ent1} ?a ?b.
      ?b ?c wd:Q{ent3}.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    """
    r = requests.get(wikidata_endpoint, params={"format": "json", "query": query})
    for result in r.json()["results"]["bindings"]:
        ent2 = result["b"]["value"].split("/Q")[-1]
        nodes.add((ent2, result["bLabel"]["value"]))
        edges.add((ent1, ent2, result["a"]["value"]))
        edges.add((ent2, ent3, result["c"]["value"]))


def wikidata_wiki_entry(entity_id):
    return f"{wikidata_root_url}wiki/Q{entity_id}"


def generate_graph(init_nodes, nodes, edges, output_file):
    dot = Digraph(comment="")
    for node in init_nodes:
        dot.node(
            str(node),
            get_node_label(node),
            color="blue",
            href=wikidata_wiki_entry(node),
        )
    for id, label in nodes:
        dot.node(id, label, color="green", href=wikidata_wiki_entry(id))
    for ent1, ent2, url in edges:
        label = url.split("/P")[-1]
        dot.edge(str(ent1), str(ent2), label=label, href=url)
    dot.render(output_file)


def get_node_label(node):
    query = f"""
    SELECT ?label WHERE {{
        wd:Q{node} rdfs:label ?label.
        FILTER(LANGMATCHES(LANG(?label), "EN")).
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}"""
    r = requests.get(wikidata_endpoint, params={"format": "json", "query": query})
    return r.json()["results"]["bindings"][0]["label"]["value"]


def main():
    parser = ArgumentParser(description="Process entity IDs")
    parser.add_argument("-n", "--nodes", nargs="+", type=int)
    parser.add_argument("-o", "--output", type=str)
    args = parser.parse_args()
    nodes = set()
    edges = set()
    for pair in permutations(args.nodes, 2):
        process_simple_connection(edges, *pair)
        process_complex_connection(nodes, edges, *pair)
    generate_graph(args.nodes, nodes, edges, args.output)


if __name__ == "__main__":
    main()
