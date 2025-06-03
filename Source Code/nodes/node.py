"""
node.py

Base abstract class representing a generic graph node used in the Patent2SDG system.
Each node has a unique ID and can store an embedding vector generated from textual content.
"""

class Node:
    def __init__(self, node_id):
        """
        Initialize the node with a unique identifier.

        Args:
            node_id (str): Unique identifier for the node (e.g., patent ID, SDG ID).
        """
        self.id = node_id
        self.embedding = None  # Vector representation of node content (computed later)

    def set_embedding(self, model, text):
        """
        Compute and set the embedding vector for this node using a language model.

        Args:
            model: Sentence embedding model (e.g., SentenceTransformer instance).
            text (str): Text content to encode into a vector.
        """
        self.embedding = model.encode(text)
