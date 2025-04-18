"""
Data simulator that generates synthetic data based on the structure defined in an OWL ontology file.
"""

from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional, Any
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD
from rdflib.term import URIRef, Literal

class OntologyDataSimulator:
    def __init__(self, owl_file_path: str, start_date: Optional[datetime] = None):
        """
        Initialize the ontology-based data simulator.
        
        Args:
            owl_file_path: Path to the OWL file containing the ontology structure
            start_date: Starting date for the simulation. Defaults to current date.
        """
        self.current_date = start_date if start_date else datetime.now()
        self.graph = Graph()
        self.graph.parse(owl_file_path)
        
        # Extract ontology structure
        self._extract_ontology_structure()
        
    def _extract_ontology_structure(self) -> None:
        """Extract classes, properties, and constraints from the OWL file."""
        self.classes = {}
        self.object_properties = {}
        self.data_properties = {}
        self.value_ranges = {}
        
        # Extract classes
        for class_uri in self.graph.subjects(RDF.type, OWL.Class):
            class_name = self._get_local_name(class_uri)
            if class_name:
                self.classes[class_name] = {
                    'uri': class_uri,
                    'label': self._get_label(class_uri),
                    'properties': []
                }
        
        # Extract properties and their domains/ranges
        for prop in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            prop_name = self._get_local_name(prop)
            if prop_name:
                domains = list(self.graph.objects(prop, RDFS.domain))
                ranges = list(self.graph.objects(prop, RDFS.range))
                self.object_properties[prop_name] = {
                    'uri': prop,
                    'label': self._get_label(prop),
                    'domains': [self._get_local_name(d) for d in domains],
                    'ranges': [self._get_local_name(r) for r in ranges]
                }
        
        for prop in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            prop_name = self._get_local_name(prop)
            if prop_name:
                domains = list(self.graph.objects(prop, RDFS.domain))
                ranges = list(self.graph.objects(prop, RDFS.range))
                self.data_properties[prop_name] = {
                    'uri': prop,
                    'label': self._get_label(prop),
                    'domains': [self._get_local_name(d) for d in domains],
                    'ranges': [self._get_local_name(r) for r in ranges]
                }
                
        # Extract value constraints and ranges
        self._extract_value_constraints()
    
    def _extract_value_constraints(self) -> None:
        """Extract value constraints for data properties."""
        XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
        
        for prop_name, prop_info in self.data_properties.items():
            constraints = {}
            prop_uri = prop_info['uri']
            
            # Get restrictions
            for restrictions in self.graph.objects(prop_uri, OWL.withRestrictions):
                for restriction in self.graph.items(restrictions):
                    # Check for min/max values
                    min_values = list(self.graph.objects(restriction, XSD.minInclusive))
                    max_values = list(self.graph.objects(restriction, XSD.maxInclusive))
                    
                    if min_values:
                        constraints['min'] = float(min_values[0])
                    if max_values:
                        constraints['max'] = float(max_values[0])
            
            # Get enumerated values
            for enum_list in self.graph.objects(prop_uri, OWL.oneOf):
                values = []
                current = enum_list
                while current:
                    first = list(self.graph.objects(current, RDF.first))
                    if first:
                        values.append(str(first[0]))
                    rest = list(self.graph.objects(current, RDF.rest))
                    current = rest[0] if rest and rest[0] != RDF.nil else None
                if values:
                    constraints['values'] = values
            
            self.value_ranges[prop_name] = constraints
    
    def _get_local_name(self, uri: URIRef) -> Optional[str]:
        """Get the local name part of a URI."""
        if not uri:
            return None
        return str(uri).split('#')[-1] if '#' in str(uri) else str(uri).split('/')[-1]
    
    def _get_label(self, uri: URIRef) -> Optional[str]:
        """Get the rdfs:label of a resource, falling back to local name."""
        labels = list(self.graph.objects(uri, RDFS.label))
        return str(labels[0]) if labels else self._get_local_name(uri)
    
    def generate_instance_data(self, class_name: str) -> Dict[str, Any]:
        """
        Generate synthetic data for an instance of the specified class.
        
        Args:
            class_name: Name of the class to generate data for
            
        Returns:
            Dict containing the generated property values
        """
        if class_name not in self.classes:
            raise ValueError(f"Unknown class: {class_name}")
        
        data = {
            'type': class_name,
            'timestamp': self.current_date.isoformat(),
            'properties': {}
        }
        
        # Generate values for data properties
        for prop_name, prop_info in self.data_properties.items():
            if class_name in prop_info['domains']:
                value = self._generate_property_value(prop_name)
                if value is not None:
                    data['properties'][prop_name] = value
        
        # Generate values for object properties
        for prop_name, prop_info in self.object_properties.items():
            if class_name in prop_info['domains']:
                related_class = prop_info['ranges'][0] if prop_info['ranges'] else None
                if related_class:
                    data['properties'][prop_name] = self._generate_related_instance(related_class)
        
        return data
    
    def _generate_property_value(self, prop_name: str) -> Any:
        """Generate a value for a property based on its constraints."""
        constraints = self.value_ranges.get(prop_name, {})
        prop_info = self.data_properties[prop_name]
        range_type = prop_info['ranges'][0] if prop_info['ranges'] else None
        
        if 'values' in constraints:
            return random.choice(constraints['values'])
        
        if 'min' in constraints or 'max' in constraints:
            min_val = constraints.get('min', 0)
            max_val = constraints.get('max', 100)
            
            if range_type == 'integer':
                return random.randint(int(min_val), int(max_val))
            return round(random.uniform(min_val, max_val), 2)
        
        # Default generation based on property range
        if range_type == 'integer':
            return random.randint(0, 100)
        elif range_type in ['decimal', 'float']:
            return round(random.uniform(0, 100), 2)
        elif range_type == 'boolean':
            return random.choice([True, False])
        elif range_type == 'dateTime':
            days = random.randint(0, 365)
            return (self.current_date + timedelta(days=days)).isoformat()
        else:
            return f"Value_{random.randint(1, 1000)}"
    
    def _generate_related_instance(self, class_name: str) -> Dict[str, Any]:
        """Generate a simplified related instance."""
        return {
            'type': class_name,
            'id': f"{class_name}_{random.randint(1, 1000)}"
        }
    
    def advance_day(self) -> None:
        """Advance the current date by one day."""
        self.current_date += timedelta(days=1)