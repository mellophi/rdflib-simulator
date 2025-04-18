"""
Module for analyzing information gain in knowledge graphs.
"""

import numpy as np
from rdflib import Graph, URIRef
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from collections import defaultdict
import math

class InformationGainAnalyzer:
    def __init__(self, graph: Graph):
        """
        Initialize the analyzer with a knowledge graph.
        
        Args:
            graph: RDFLib Graph to analyze
        """
        self.graph = graph
        
    def calculate_node_entropy(self, node: URIRef) -> float:
        """
        Calculate the entropy of a node based on its connections.
        Higher entropy indicates more diverse connections.
        
        Args:
            node: The node to calculate entropy for
            
        Returns:
            float: Entropy value
        """
        # Get all predicates connected to this node
        predicates = set()
        for _, p, _ in self.graph.triples((node, None, None)):
            predicates.add(str(p))
        for _, p, _ in self.graph.triples((None, None, node)):
            predicates.add(str(p))
            
        if not predicates:
            return 0.0
            
        # Calculate probability distribution of predicates
        pred_counts = defaultdict(int)
        total_connections = 0
        
        for p in predicates:
            count = len(list(self.graph.triples((node, URIRef(p), None))))
            count += len(list(self.graph.triples((None, URIRef(p), node))))
            pred_counts[p] = count
            total_connections += count
            
        # Calculate entropy using Shannon's formula
        entropy = 0.0
        for count in pred_counts.values():
            prob = count / total_connections
            entropy -= prob * math.log2(prob)
            
        return entropy
        
    def calculate_information_gain(self, node_type: str, 
                                 before_graph: Graph, 
                                 after_graph: Graph) -> float:
        """
        Calculate information gain for nodes of a specific type
        between two graph states.
        
        Args:
            node_type: Type of nodes to analyze ('health' or 'travel')
            before_graph: Graph state before
            after_graph: Graph state after
            
        Returns:
            float: Information gain value
        """
        # Get nodes of specified type
        nodes_before = set()
        nodes_after = set()
        
        for s, p, o in before_graph:
            if node_type in str(s):
                nodes_before.add(s)
            if node_type in str(o):
                nodes_before.add(o)
                
        for s, p, o in after_graph:
            if node_type in str(s):
                nodes_after.add(s)
            if node_type in str(o):
                nodes_after.add(o)
                
        # Calculate average entropy before and after
        entropy_before = sum(self.calculate_node_entropy(n) for n in nodes_before)
        entropy_after = sum(self.calculate_node_entropy(n) for n in nodes_after)
        
        # Normalize by number of nodes
        if nodes_before:
            entropy_before /= len(nodes_before)
        if nodes_after:
            entropy_after /= len(nodes_after)
            
        return max(0, entropy_after)
        
    def plot_information_gain_comparison(self, 
                                       health_gains: List[float],
                                       travel_gains: List[float],
                                       timestamps: List[str],
                                       output_file: str = None):
        """
        Plot comparison of information gain between health and travel data.
        
        Args:
            health_gains: List of health-related information gains
            travel_gains: List of travel-related information gains
            timestamps: List of timestamps or labels for x-axis
            output_file: Optional file path to save the plot
        """
        plt.figure(figsize=(12, 6))
        
        x = np.arange(len(timestamps))
        width = 0.35
        
        plt.bar(x - width/2, health_gains, width, label='Health Data',
               color='#2ecc71', alpha=0.7)
        plt.bar(x + width/2, travel_gains, width, label='Travel Data',
               color='#3498db', alpha=0.7)
        
        plt.xlabel('Time')
        plt.ylabel('Information Gain')
        plt.title('Comparison of Information Gain: Health vs Travel Data')
        plt.xticks(x, timestamps, rotation=45)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
        else:
            plt.show() 