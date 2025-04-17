"""
Knowledge Graph visualization module using NetworkX and Matplotlib.
"""

import networkx as nx
import matplotlib.pyplot as plt
from rdflib import Graph, URIRef, Literal
from typing import Optional, Dict, Any
import re

class KnowledgeGraphVisualizer:
    def __init__(self, figsize: tuple = (16, 10)):
        """
        Initialize the visualizer.
        
        Args:
            figsize: Figure size for the plot
        """
        self.figsize = figsize
        self.colors = {
            'health': '#2ecc71',  # green
            'travel': '#3498db',  # blue
            'location': '#e74c3c',  # red
            'literal': '#95a5a6',  # gray
            'other': '#9b59b6'    # purple
        }
        
    def _get_node_color(self, node_uri: str) -> str:
        """Get color for a node based on its type."""
        if isinstance(node_uri, Literal):
            return self.colors['literal']
        
        uri = str(node_uri)
        if 'health' in uri:
            return self.colors['health']
        elif 'travel' in uri:
            return self.colors['travel']
        elif 'location' in uri:
            return self.colors['location']
        return self.colors['other']
    
    def _get_short_name(self, uri: str) -> str:
        """Extract a short readable name from a URI or Literal."""
        if isinstance(uri, Literal):
            return str(uri)
        
        # Convert URI to string if it's a URIRef
        uri_str = str(uri)
        
        # Try to get the last part of the URI after the last / or #
        name = uri_str.split('/')[-1].split('#')[-1]
        
        # If it's a UUID, try to extract meaningful part before it
        if re.match(r'.*[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}.*', name):
            parts = name.split('_')
            if len(parts) > 1:
                return parts[0]
        
        return name

    def visualize_graph(self, graph: Graph, output_file: Optional[str] = None,
                       show_labels: bool = True, node_size: int = 2000,
                       with_labels: bool = True) -> None:
        """
        Visualize the RDF graph using NetworkX and Matplotlib.
        
        Args:
            graph: RDFLib Graph to visualize
            output_file: Optional file path to save the visualization
            show_labels: Whether to show edge labels
            node_size: Size of nodes in the visualization
            with_labels: Whether to show node labels
        """
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes and edges
        for s, p, o in graph:
            # Add nodes
            if not isinstance(s, Literal) and not G.has_node(s):
                G.add_node(s, color=self._get_node_color(s))
            if not isinstance(o, Literal) and not G.has_node(o):
                G.add_node(o, color=self._get_node_color(o))
            
            # Add edges (skip if either end is a literal)
            if not isinstance(s, Literal) and not isinstance(o, Literal):
                G.add_edge(s, o, label=self._get_short_name(p))

        # Get node colors
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        
        # Create the plot
        plt.figure(figsize=self.figsize)
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                             node_size=node_size)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos)
        
        # Draw node labels
        if with_labels:
            labels = {node: self._get_short_name(node) for node in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        # Draw edge labels
        if show_labels:
            edge_labels = nx.get_edge_attributes(G, 'label')
            nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6)
        
        plt.title("Knowledge Graph Visualization")
        plt.axis('off')
        
        # Save or show the plot
        if output_file:
            plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
        else:
            plt.show()
            
    def visualize_subgraph(self, graph: Graph, focus_node: str,
                          depth: int = 2, output_file: Optional[str] = None) -> None:
        """
        Visualize a subgraph centered around a specific node.
        
        Args:
            graph: RDFLib Graph to visualize
            focus_node: URI of the node to focus on
            depth: How many steps out from the focus node to include
            output_file: Optional file path to save the visualization
        """
        # Create NetworkX graph for the full graph first
        G = nx.Graph()
        
        # Convert focus_node to URIRef if it's a string
        if isinstance(focus_node, str):
            focus_node = URIRef(focus_node)
        
        # Add all nodes and edges
        for s, p, o in graph:
            if not isinstance(s, Literal) and not isinstance(o, Literal):
                G.add_edge(s, o, label=self._get_short_name(p))
        
        # Get the subgraph nodes using BFS
        nodes = {focus_node}
        current_nodes = {focus_node}
        
        for _ in range(depth):
            next_nodes = set()
            for node in current_nodes:
                next_nodes.update(G.neighbors(node))
            nodes.update(next_nodes)
            current_nodes = next_nodes
        
        # Create the subgraph
        subgraph = G.subgraph(nodes)
        
        # Prepare the visualization
        plt.figure(figsize=self.figsize)
        pos = nx.spring_layout(subgraph, k=1, iterations=50)
        
        # Draw nodes with colors
        node_colors = [self._get_node_color(node) for node in subgraph.nodes()]
        nx.draw_networkx_nodes(subgraph, pos, node_color=node_colors,
                             node_size=2000)
        
        # Highlight the focus node
        nx.draw_networkx_nodes(subgraph, pos, nodelist=[focus_node],
                             node_color='yellow', node_size=3000)
        
        # Draw edges
        nx.draw_networkx_edges(subgraph, pos)
        
        # Draw labels
        labels = {node: self._get_short_name(node) for node in subgraph.nodes()}
        nx.draw_networkx_labels(subgraph, pos, labels, font_size=8)
        
        edge_labels = nx.get_edge_attributes(subgraph, 'label')
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels, font_size=6)
        
        plt.title(f"Subgraph around {self._get_short_name(focus_node)}")
        plt.axis('off')
        
        # Save or show the plot
        if output_file:
            plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
        else:
            plt.show() 