"""
Module for simulating data based on custom ontologies.
"""

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from typing import Dict, List, Any, Optional, Tuple
import random
import re
from datetime import datetime
from .ontology_builder import OntologyBuilder

class OntologyBasedSimulator:
    def __init__(self, 
                 base_uri: str = "http://example.org/",
                 custom_ontology_path: Optional[str] = None):
        """
        Initialize the ontology-based simulator.
        
        Args:
            base_uri: Base URI for the generated data
            custom_ontology_path: Path to custom ontology file (supports various RDF formats)
        """
        self.base_uri = base_uri
        self.ontology_builder = OntologyBuilder()
        
        # Load custom ontology if provided
        if custom_ontology_path:
            self.load_custom_ontology(custom_ontology_path)
            
        # Initialize ontology analysis results
        self.classes = {}  # class URI -> properties
        self.properties = {}  # property URI -> range, domain
        self.value_constraints = {}  # property URI -> constraints
        self.analyzed = False
        
    def load_custom_ontology(self, ontology_path: str) -> None:
        """
        Load a custom ontology from file.
        
        Args:
            ontology_path: Path to the ontology file
        """
        format_map = {
            '.ttl': 'turtle',
            '.n3': 'n3',
            '.xml': 'xml',
            '.rdf': 'xml',
            '.owl': 'turtle',
            '.nt': 'nt'
        }
        
        # Determine format from file extension
        ext = re.search(r'\.[^.]+$', ontology_path)
        format = format_map.get(ext.group() if ext else '', 'xml')
        
        # Load the ontology
        self.ontology_builder.get_graph_manager().graph.parse(
            ontology_path, format=format)
        
    def analyze_ontology(self) -> None:
        """
        Analyze the loaded ontology to extract classes, properties, and constraints.
        """
        graph = self.ontology_builder.get_graph_manager().graph
        
        # Get all classes
        for class_uri in graph.subjects(RDF.type, OWL.Class):
            self.classes[class_uri] = {
                'label': self._get_label(class_uri),
                'properties': [],
                'subclass_of': list(graph.objects(class_uri, RDFS.subClassOf))
            }
            
        # Get all properties and their characteristics
        for prop in graph.subjects(RDF.type, OWL.DatatypeProperty):
            self._analyze_property(prop, 'datatype')
            
        for prop in graph.subjects(RDF.type, OWL.ObjectProperty):
            self._analyze_property(prop, 'object')
            
        # Analyze property constraints
        self._analyze_constraints()
        
        self.analyzed = True
        
    def _analyze_property(self, prop_uri: URIRef, prop_type: str) -> None:
        """
        Analyze a property's characteristics.
        
        Args:
            prop_uri: URI of the property
            prop_type: Type of property ('datatype' or 'object')
        """
        graph = self.ontology_builder.get_graph_manager().graph
        
        domains = list(graph.objects(prop_uri, RDFS.domain))
        ranges = list(graph.objects(prop_uri, RDFS.range))
        
        self.properties[prop_uri] = {
            'type': prop_type,
            'label': self._get_label(prop_uri),
            'domains': domains,
            'ranges': ranges,
            'functional': (prop_uri, RDF.type, OWL.FunctionalProperty) in graph
        }
        
        # Add property to its domain classes
        for domain in domains:
            if domain in self.classes:
                self.classes[domain]['properties'].append(prop_uri)
                
    def _analyze_constraints(self) -> None:
        """
        Analyze property constraints from the ontology.
        """
        graph = self.ontology_builder.get_graph_manager().graph
        
        # Look for common constraint patterns
        for prop_uri in self.properties:
            constraints = {
                'min_value': None,
                'max_value': None,
                'allowed_values': set(),
                'pattern': None
            }
            
            # Check for XML Schema constraints
            for restriction in graph.subjects(OWL.onProperty, prop_uri):
                if (restriction, RDF.type, OWL.Restriction) in graph:
                    self._extract_restriction_constraints(restriction, constraints)
                    
            if constraints['min_value'] is not None or \
               constraints['max_value'] is not None or \
               constraints['allowed_values'] or \
               constraints['pattern'] is not None:
                self.value_constraints[prop_uri] = constraints
                
    def _extract_restriction_constraints(self, 
                                       restriction: URIRef, 
                                       constraints: Dict) -> None:
        """
        Extract constraints from an OWL restriction.
        
        Args:
            restriction: URI of the restriction
            constraints: Dictionary to update with found constraints
        """
        graph = self.ontology_builder.get_graph_manager().graph
        
        # Check for cardinality constraints
        min_card = graph.value(restriction, OWL.minCardinality)
        max_card = graph.value(restriction, OWL.maxCardinality)
        
        if min_card:
            constraints['min_value'] = int(min_card)
        if max_card:
            constraints['max_value'] = int(max_card)
            
        # Check for value constraints
        for value in graph.objects(restriction, OWL.hasValue):
            constraints['allowed_values'].add(value)
            
    def _get_label(self, uri: URIRef) -> str:
        """Get label for a URI, falling back to local name if no label exists."""
        graph = self.ontology_builder.get_graph_manager().graph
        label = graph.value(uri, RDFS.label)
        if label:
            return str(label)
        return uri.split('#')[-1] if '#' in uri else uri.split('/')[-1]
        
    def generate_instance(self, class_uri: URIRef, 
                         instance_id: str = None) -> None:
        """
        Generate an instance of a class with valid property values.
        
        Args:
            class_uri: URI of the class to instantiate
            instance_id: Optional identifier for the instance
        """
        if not self.analyzed:
            self.analyze_ontology()
            
        if class_uri not in self.classes:
            raise ValueError(f"Class {class_uri} not found in ontology")
            
        # Create instance URI
        if instance_id is None:
            instance_id = f"instance_{random.randint(1000, 9999)}"
        instance_uri = URIRef(f"{self.base_uri}{instance_id}")
        
        # Add type assertion
        self.ontology_builder.get_graph_manager().add_triple(
            instance_uri, "rdf:type", class_uri)
            
        # Generate values for properties
        for prop_uri in self.classes[class_uri]['properties']:
            self._generate_property_value(instance_uri, prop_uri)
            
    def _generate_property_value(self, 
                               subject_uri: URIRef, 
                               prop_uri: URIRef) -> None:
        """
        Generate and add a value for a property.
        
        Args:
            subject_uri: URI of the subject
            prop_uri: URI of the property
        """
        prop_info = self.properties[prop_uri]
        constraints = self.value_constraints.get(prop_uri, {})
        
        if prop_info['type'] == 'datatype':
            value = self._generate_datatype_value(prop_info['ranges'][0], constraints)
            if value is not None:
                self.ontology_builder.get_graph_manager().add_triple(
                    subject_uri, prop_uri, value)
        else:
            # For object properties, create or reference another instance
            range_class = prop_info['ranges'][0]
            self.generate_instance(range_class)
            
    def _generate_datatype_value(self, 
                                datatype: URIRef, 
                                constraints: Dict) -> Optional[Literal]:
        """
        Generate a value for a datatype property.
        
        Args:
            datatype: URI of the datatype
            constraints: Constraints to apply to the value
            
        Returns:
            Generated value as a Literal
        """
        if constraints.get('allowed_values'):
            return random.choice(list(constraints['allowed_values']))
            
        min_val = constraints.get('min_value', 0)
        max_val = constraints.get('max_value', 100)
        
        if 'integer' in str(datatype).lower():
            return Literal(random.randint(min_val, max_val))
        elif 'float' in str(datatype).lower() or 'decimal' in str(datatype).lower():
            return Literal(random.uniform(min_val, max_val))
        elif 'string' in str(datatype).lower():
            return Literal(f"Value_{random.randint(1000, 9999)}")
        elif 'date' in str(datatype).lower():
            return Literal(datetime.now().date().isoformat())
        
        return None
        
    def simulate_data(self, 
                     class_uri: URIRef, 
                     num_instances: int = 1,
                     base_id: str = None) -> None:
        """
        Simulate multiple instances of a class.
        
        Args:
            class_uri: URI of the class to instantiate
            num_instances: Number of instances to generate
            base_id: Base identifier for generated instances
        """
        for i in range(num_instances):
            instance_id = f"{base_id}_{i}" if base_id else None
            self.generate_instance(class_uri, instance_id)
            
    def export_generated_data(self, 
                            format: str = 'turtle', 
                            file_path: Optional[str] = None) -> Optional[str]:
        """
        Export the generated data.
        
        Args:
            format: Format to export (turtle, xml, n3, etc.)
            file_path: Path to save the exported data
            
        Returns:
            Optional[str]: String representation if no file_path is provided
        """
        return self.ontology_builder.get_graph_manager().export_graph(
            format, file_path) 