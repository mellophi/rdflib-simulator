# RDFLib Knowledge Graph Simulator

A Python-based knowledge graph simulator that creates and manipulates ontologies similar to WikiData and DBpedia using RDFLib.

## Features

- Create and manage RDF-based knowledge graphs
- Import and export data in various RDF formats (N-Triples, Turtle, RDF/XML)
- Query graphs using SPARQL
- Visualize knowledge graphs
- Generate synthetic data based on ontology patterns
- Support for common ontology patterns and vocabularies
- Information gain analysis for tracking knowledge evolution
- Comparative analysis between different types of data (health, travel, etc.)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/rdflib-simulator.git
cd rdflib-simulator
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```
or
```bash
pip install -e .
```

## Project Structure

```
rdflib-simulator/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph_manager.py
│   │   ├── ontology_builder.py
│   │   └── personal_data_simulator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── data_simulator.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   └── information_gain.py
│   └── visualization/
│       ├── __init__.py
│       └── visualizer.py
├── tests/
│   └── __init__.py
├── examples/
│   ├── analyze_information_gain.py
│   ├── simulate_personal_data.py
│   └── visualize_graph.py
├── data/
│   └── README.md
├── requirements.txt
└── README.md
```

## Usage

### Basic Knowledge Graph Creation

```python
from src.core.personal_data_simulator import PersonalDataKnowledgeSimulator
from datetime import datetime

# Initialize simulator
simulator = PersonalDataKnowledgeSimulator(
    person_id="person123",
    start_date=datetime.now()
)

# Simulate data for multiple days
simulator.simulate_period(days=7)

# Export the ontology
simulator.export_ontology(format='turtle', file_path='data/personal_data.ttl')
```

### Information Gain Analysis

The simulator includes functionality to analyze how information content evolves over time. This is particularly useful for:
- Tracking the growth of knowledge in different domains
- Comparing information gain between different types of data
- Identifying patterns in data accumulation

```python
from src.analysis.information_gain import InformationGainAnalyzer
from datetime import datetime

# Initialize simulator and analyzer
simulator = PersonalDataKnowledgeSimulator("person123", datetime.now())
analyzer = InformationGainAnalyzer(simulator.ontology_builder.get_graph_manager().graph)

# Simulate data and analyze information gain
simulator.simulate_day()
graph_before = simulator.ontology_builder.get_graph_manager().graph.copy()

simulator.simulate_day()
graph_after = simulator.ontology_builder.get_graph_manager().graph

# Calculate information gain for different types of data
health_gain = analyzer.calculate_information_gain('health', graph_before, graph_after)
travel_gain = analyzer.calculate_information_gain('travel', graph_before, graph_after)

# Visualize the comparison
analyzer.plot_information_gain_comparison(
    health_gains=[health_gain],
    travel_gains=[travel_gain],
    timestamps=['2024-03-20'],
    output_file="data/information_gain.png"
)
```

### Visualization

```python
from src.visualization.visualizer import KnowledgeGraphVisualizer

# Initialize visualizer
visualizer = KnowledgeGraphVisualizer(simulator.ontology_builder.get_graph_manager().graph)

# Visualize the complete graph
visualizer.visualize_graph(output_file="data/complete_graph.png")

# Visualize a subgraph around a specific node
visualizer.visualize_subgraph(
    focus_node="http://example.org/personal/health/vitals_person123_2024-03-20",
    output_file="data/health_subgraph.png"
)
```

## Analysis Features

### Information Gain Analysis

The `InformationGainAnalyzer` class provides tools to:
- Calculate entropy-based information content of nodes
- Measure information gain between graph states
- Compare information evolution across different data types
- Visualize information gain patterns

Two main analysis scenarios are provided:
1. **Regular Data Addition**: Analyzes steady accumulation of knowledge
2. **Burst Data Addition**: Analyzes periodic spikes in information content

### Visualization Features

The visualization module supports:
- Full graph visualization with color-coded nodes
- Subgraph visualization focused on specific nodes
- Comparative information gain plots
- Custom styling and layout options

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 