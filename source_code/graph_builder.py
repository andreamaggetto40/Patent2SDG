"""
graph_builder.py

Responsible for initializing a base graph with SDG nodes.
This module is part of the Patent2SDG system.
"""

import networkx as nx

def build_sdg_graph(sdgs):
    """
    Initializes an undirected graph containing nodes for each Sustainable Development Goal (SDG).

    Args:
        sdgs (List[SDGNode]): A list of SDGNode objects, each expected to have 'id', 'name', and 'description' attributes.

    Returns:
        networkx.Graph: A graph where each node represents an SDG with attached metadata.
    """
    G = nx.Graph()  # Create an empty undirected graph

    # Add each SDG as a node in the graph, with label and description for visualization and context
    for sdg in sdgs:
        G.add_node(sdg.id, label=sdg.name, description=sdg.description)

    return G
