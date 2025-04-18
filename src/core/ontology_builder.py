"""
OntologyBuilder class for creating ontologies with common patterns.
"""

from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Optional, List, Dict, Union
from .graph_manager import GraphManager

class OntologyBuilder:
    def __init__(self, graph_manager: Optional[GraphManager] = None):
        """
        Initialize a new OntologyBuilder instance.
        
        Args:
            graph_manager (Optional[GraphManager]): Existing GraphManager instance or None to create new
        """
        self.gm = graph_manager if graph_manager else GraphManager()
        
    def create_class(self, class_name: str, label: Optional[str] = None,
                    comment: Optional[str] = None,
                    superclass: Optional[str] = None) -> None:
        """
        Create a new class in the ontology.
        
        Args:
            class_name (str): Name of the class
            label (Optional[str]): Human-readable label for the class
            comment (Optional[str]): Description of the class
            superclass (Optional[str]): Parent class URI
        """
        class_uri = class_name
        self.gm.add_triple(class_uri, RDF.type, OWL.Class.toPython())
        
        if label:
            self.gm.add_triple(class_uri, RDFS.label, label, XSD.string.toPython())
        
        if comment:
            self.gm.add_triple(class_uri, RDFS.comment, comment, XSD.string.toPython())
            
        if superclass:
            self.gm.add_triple(class_uri, RDFS.subClassOf, superclass)

    def create_property(self, property_name: str, 
                       property_type: str = "ObjectProperty",
                       domain: Optional[str] = None,
                       range_: Optional[str] = None,
                       label: Optional[str] = None,
                       comment: Optional[str] = None) -> None:
        """
        Create a new property in the ontology.
        
        Args:
            property_name (str): Name of the property
            property_type (str): Type of property (ObjectProperty or DatatypeProperty)
            domain (Optional[str]): Domain class URI
            range_ (Optional[str]): Range class URI or datatype
            label (Optional[str]): Human-readable label
            comment (Optional[str]): Description of the property
        """
        property_uri = property_name
        
        if property_type == "ObjectProperty":
            self.gm.add_triple(property_uri, RDF.type, OWL.ObjectProperty.toPython())
        else:
            self.gm.add_triple(property_uri, RDF.type, OWL.DatatypeProperty.toPython())
            
        if domain:
            self.gm.add_triple(property_uri, RDFS.domain, domain)
            
        if range_:
            self.gm.add_triple(property_uri, RDFS.range, range_)
            
        if label:
            self.gm.add_triple(property_uri, RDFS.label, label, XSD.string.toPython())
            
        if comment:
            self.gm.add_triple(property_uri, RDFS.comment, comment, XSD.string.toPython())

    def create_individual(self, individual_name: str, 
                         class_uri: str,
                         label: Optional[str] = None,
                         properties: Optional[Dict[str, Union[str, int, float, bool]]] = None) -> None:
        """
        Create a new individual (instance) in the ontology.
        
        Args:
            individual_name (str): Name of the individual
            class_uri (str): URI of the class this individual belongs to
            label (Optional[str]): Human-readable label
            properties (Optional[Dict]): Dictionary of property-value pairs
        """
        individual_uri = individual_name
        self.gm.add_triple(individual_uri, RDF.type, class_uri)
        
        if label:
            self.gm.add_triple(individual_uri, RDFS.label, label, XSD.string.toPython())
            
        if properties:
            for prop, value in properties.items():
                self.gm.add_triple(individual_uri, prop, value)

    def create_restriction(self, on_property: str,
                         restriction_type: str,
                         value: Union[str, int],
                         class_uri: Optional[str] = None) -> str:
        """
        Create a property restriction.
        
        Args:
            on_property (str): URI of the property to restrict
            restriction_type (str): Type of restriction (someValuesFrom, allValuesFrom, etc.)
            value: Value for the restriction
            class_uri (Optional[str]): Class to apply the restriction to
            
        Returns:
            str: URI of the created restriction
        """
        restriction = BNode()
        self.gm.add_triple(str(restriction), RDF.type, OWL.Restriction.toPython())
        self.gm.add_triple(str(restriction), OWL.onProperty, on_property)
        
        restriction_uri = f"owl:{restriction_type}"
        self.gm.add_triple(str(restriction), restriction_uri, str(value))
        
        if class_uri:
            self.gm.add_triple(class_uri, RDFS.subClassOf, str(restriction))
            
        return str(restriction)

    def add_axiom(self, subject: str, axiom_type: str, object_: str) -> None:
        """
        Add an OWL axiom to the ontology.
        
        Args:
            subject (str): Subject of the axiom
            axiom_type (str): Type of axiom (e.g., equivalentClass, disjointWith)
            object_ (str): Object of the axiom
        """
        axiom_uri = f"owl:{axiom_type}"
        self.gm.add_triple(subject, axiom_uri, object_)

    def get_graph_manager(self) -> GraphManager:
        """
        Get the underlying GraphManager instance.
        
        Returns:
            GraphManager: The graph manager instance
        """
        return self.gm 