import json
import networkx as nx
import matplotlib.pyplot as plt
import random
from networkx.drawing.nx_agraph import graphviz_layout

# Load JSON data
with open("output.json", "r") as input_file:
    json_data_list = []
    for line in input_file:
        json_data_list.append(json.loads(line))

company_graph = nx.Graph()
entity_list = ["Owner Name", "Registered Agent", "Commercial Registered Agent"]

for data_item in json_data_list:
    company_name = data_item[1]["TITLE"][0].split("\n")[0]
    for detail_item in data_item[1]["Additional information"]["DRAWER_DETAIL_LIST"]:
        if detail_item["LABEL"] in entity_list:
            entity_info = detail_item["VALUE"].split("\n")[0]
            company_graph.add_edge(company_name, entity_info)

min_count, labels_on = 2, True

# Draw graph with company names in white boxes as nodes
plt.figure(1, figsize=(30, 30))
node_pos = graphviz_layout(company_graph, prog="neato")
company_node_list = [node for node in company_graph.nodes() if node not in entity_list]
nx.draw_networkx(
    company_graph,
    node_pos,
    nodelist=company_node_list,
    node_size=20,
    node_color="white",
    edgecolors="black",
    with_labels=True,
    labels={node: node for node in company_node_list},
    bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"),
)
plt.title(f"Graph with Company Names")
plt.savefig("output_graph_company_names.png", dpi=300, bbox_inches="tight")
plt.show()

# Draw atlas graph without names and with different colored subgraphs
plt.figure(2, figsize=(8, 8))
connected_subgraphs = (
    company_graph.subgraph(c) for c in nx.connected_components(company_graph)
)
num_edges_total = 0
for connected_subgraph in connected_subgraphs:
    random_color = [random.random()] * nx.number_of_nodes(connected_subgraph)
    if len(connected_subgraph.nodes()) > min_count:
        nx.draw(
            connected_subgraph,
            node_pos,
            node_size=40,
            node_color=random_color,
            vmin=0.0,
            vmax=1.0,
            with_labels=False,
            bbox=dict(facecolor="whitesmoke"),
        )
        num_edges_total += 1

plt.title(
    f"Atlas Graph without Names: There are {num_edges_total} Edges with a Node Count Greater than {min_count}."
)
plt.savefig("output_graph_atlas.png", dpi=300, bbox_inches="tight")
plt.show()
plt.close()
