from itertools import combinations
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .node import Node

class OpportunityNode(Node):
    def __init__(self, opportunity_id, label):
        super().__init__(opportunity_id)
        self.label = label

    @staticmethod
    def generate_shared_opportunity_nodes(patent_embeddings, threshold=0.6):
        """
        Create OpportunityNodes based on high cosine similarity between patents.
        Uses average vector of the group as semantic center.
        """
        groups = []
        used = set()

        for (k1, v1), (k2, v2) in combinations(patent_embeddings.items(), 2):
            sim = cosine_similarity([v1], [v2])[0][0]
            if sim >= threshold:
                group = set([k1, k2])
                if not any(group <= g for g in groups):
                    groups.append(group)
                used |= group

        opportunity_nodes = []
        connections = {}

        for idx, group in enumerate(groups, start=1):
            vecs = [patent_embeddings[pid] for pid in group]
            center = np.mean(vecs, axis=0)

            opp_id = f"OPPORTUNITY_{idx}"
            label = f"Shared Opportunity {idx} ({len(group)} patents)"
            node = OpportunityNode(opp_id, label)
            node.embedding = center
            opportunity_nodes.append(node)
            connections[opp_id] = group

        return opportunity_nodes, connections