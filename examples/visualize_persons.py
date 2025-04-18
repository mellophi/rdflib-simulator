"""
Example script demonstrating how to visualize the generated Person instances
using the KnowledgeGraphVisualizer.
"""

from rdflib import Graph
from src.visualization.visualizer import KnowledgeGraphVisualizer

def main():
    # Load the generated data
    graph = Graph()
    graph.parse("data/generated_persons.ttl", format="turtle")

    # Initialize the visualizer
    visualizer = KnowledgeGraphVisualizer()

    # Visualize the entire graph
    print("Generating visualization of all Person instances...")
    visualizer.visualize_graph(
        graph,
        output_file="data/person_graph.png",
        show_labels=True,
        title="Generated Person Instances"
    )
    print("Visualization saved to data/person_graph.png")

    # You can also visualize a specific person and their properties
    # by using the visualize_subgraph method with a specific subject URI
    print("\nTo visualize a specific person, you can use:")
    print("visualizer.visualize_subgraph(graph, person_uri, depth=1)")

if __name__ == "__main__":
    main() 