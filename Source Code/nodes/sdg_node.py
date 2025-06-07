"""
sdg_node.py

Defines SDGNode, a specialized node representing a United Nations Sustainable Development Goal.
Each SDG node includes a name and description used for semantic matching and graph construction.
"""

from .node import Node

class SDGNode(Node):
    def __init__(self, sdg_id, name, description):
        """
        Initialize an SDG node.

        Args:
            sdg_id (str): Unique identifier (e.g., 'SDG13').
            name (str): Name of the SDG (e.g., 'Climate Action').
            description (str): Full textual description used for semantic matching.
        """
        super().__init__(sdg_id)
        self.name = name
        self.description = description
