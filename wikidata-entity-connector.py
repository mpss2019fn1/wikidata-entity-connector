from argparse import ArgumentParser
from itertools import permutations

import requests
from graphviz import Digraph

wikidata_root_url = "https://www.wikidata.org/"
wikidata_query_endpoint = "https://query.wikidata.org/sparql"


def process_simple_connection(edges, ent1, ent2):
    query = f"SELECT ?a WHERE {{wd:Q{ent1} ?a wd:Q{ent2}.}}"
    r = requests.get(wikidata_query_endpoint, params={"format": "json", "query": query})
    for query_result in r.json()["results"]["bindings"]:
        edges.add((ent1, ent2, query_result["a"]["value"]))


def process_complex_connection(nodes, edges, ent1, ent3):
    query = f"""
    SELECT ?a ?b ?bLabel ?c WHERE {{
      wd:Q{ent1} ?a ?b.
      ?b ?c wd:Q{ent3}.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    """
    r = requests.get(wikidata_query_endpoint, params={"format": "json", "query": query})
    for query_result in r.json()["results"]["bindings"]:
        ent2 = query_result["b"]["value"].split("/Q")[-1]
        nodes.add((ent2, query_result["bLabel"]["value"]))
        edges.add((ent1, ent2, query_result["a"]["value"]))
        edges.add((ent2, ent3, query_result["c"]["value"]))


def wikidata_wiki_entry(entity_id):
    return f"{wikidata_root_url}wiki/Q{entity_id}"


def generate_graph(init_nodes, intermediate_nodes, edges, output_file):
    dot = Digraph(comment="")
    for node_id in init_nodes:
        dot.node(
            str(node_id),
            get_node_label(node_id),
            color="blue",
            href=wikidata_wiki_entry(node_id),
        )
    for node_id, node_label in intermediate_nodes:
        dot.node(node_id, node_label, color="green", href=wikidata_wiki_entry(node_id))
    for ent1, ent2, url in edges:
        node_label = url.split("/P")[-1]
        dot.edge(str(ent1), str(ent2), label=node_label, href=url)
    dot.render(output_file)


def get_node_label(node):
    query = f"""
    SELECT ?label WHERE {{
        wd:Q{node} rdfs:label ?label.
        FILTER(LANGMATCHES(LANG(?label), "EN")).
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}"""
    r = requests.get(wikidata_query_endpoint, params={"format": "json", "query": query})
    return r.json()["results"]["bindings"][0]["label"]["value"]


def main():
    parser = ArgumentParser(description="Process entity IDs")
    parser.add_argument("-n", "--nodes", nargs="+", type=int, help="integers to represent wikidata items (without prefix)")
    parser.add_argument("-o", "--output", type=str, help="file to store the output")
    args = parser.parse_args()
    nodes = set()
    edges = set()
    for pair in permutations(args.nodes, 2):
        process_simple_connection(edges, *pair)
        process_complex_connection(nodes, edges, *pair)
    generate_graph(args.nodes, nodes, edges, args.output)


if __name__ == "__main__":
    main()
