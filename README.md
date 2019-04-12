# Wikidata Entity Connector

This is a tiny script to generate a graph, which visualise the relations of given [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) entities.

## Usage

`python wikidata-entity-connector.py -n NODES -o OUTPUT`

---

**Example:**
`python wikidata-entity-connector.py -n 567 1196 56039 154797 -o output.gv`

This call will generate a [Graphviz Dot File](https://www.graphviz.org/doc/info/lang.html) (output.gv) and a graph visualization in PDF format (output.gv.pdf).
