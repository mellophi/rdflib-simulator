"""
GraphManager class for managing RDF graphs.
"""

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
from typing import Optional, List, Dict, Union, Tuple
import json
import urllib.parse

class GraphManager:
    def __init__(self, base_uri: str = "http://example.org/"):
        """
        Initialize a new GraphManager instance.
        
        Args:
            base_uri (str): Base URI for the knowledge graph
        """
        self.graph = Graph()
        self.base_uri = base_uri if base_uri.endswith('/') else base_uri + '/'
        self.base = Namespace(self.base_uri)
        
        # Bind common namespaces
        self.graph.bind('rdf', RDF)
        self.graph.bind('rdfs', RDFS)
        self.graph.bind('owl', OWL)
        self.graph.bind('xsd', XSD)
        self.graph.bind('base', self.base)

    def _create_uri_or_literal(self, value: Union[str, int, float, bool],
                             datatype: Optional[str] = None) -> Union[URIRef, Literal]:
        """
        Create a URIRef or Literal based on the value type and context.
        
        Args:
            value: The value to convert
            datatype: Optional XSD datatype for literals
            
        Returns:
            URIRef or Literal
        """
        if isinstance(value, (int, float, bool)):
            return Literal(value)
        elif isinstance(value, str):
            if datatype:
                return Literal(value, datatype=URIRef(datatype))
            elif value.startswith('http'):
                return URIRef(value)
            elif ':' in value:  # Namespace prefix
                return URIRef(value)
            else:
                return Literal(value)
        return value

    def add_triple(self, subject: str, predicate: str, obj: Union[str, int, float, bool],
                  datatype: Optional[str] = None) -> None:
        """
        Add a triple to the graph.
        
        Args:
            subject (str): Subject of the triple
            predicate (str): Predicate of the triple
            obj (Union[str, int, float, bool]): Object of the triple
            datatype (Optional[str]): XSD datatype for literal values
        """
        # Handle subject
        if ':' in subject:
            s = URIRef(subject)
        else:
            s = URIRef(self.base_uri + urllib.parse.quote(subject))
            
        # Handle predicate
        if ':' in predicate:
            p = URIRef(predicate)
        else:
            p = URIRef(self.base_uri + urllib.parse.quote(predicate))
            
        # Handle object
        if isinstance(obj, (URIRef, Literal)):
            o = obj
        else:
            o = self._create_uri_or_literal(obj, datatype)
            
        self.graph.add((s, p, o))

    def remove_triple(self, subject: str, predicate: str, obj: str) -> None:
        """
        Remove a triple from the graph.
        
        Args:
            subject (str): Subject of the triple
            predicate (str): Predicate of the triple
            obj (str): Object of the triple
        """
        s = URIRef(self.base_uri + subject) if not subject.startswith('http') else URIRef(subject)
        p = URIRef(self.base_uri + predicate) if not predicate.startswith('http') else URIRef(predicate)
        o = URIRef(self.base_uri + obj) if not obj.startswith('http') else URIRef(obj)
        
        self.graph.remove((s, p, o))

    def query_graph(self, sparql_query: str) -> List[Dict]:
        """
        Query the graph using SPARQL.
        
        Args:
            sparql_query (str): SPARQL query string
            
        Returns:
            List[Dict]: Query results as a list of dictionaries
        """
        results = []
        qres = self.graph.query(sparql_query)
        
        for row in qres:
            result = {}
            for var, value in zip(qres.vars, row):
                result[var.toPython()] = value.toPython()
            results.append(result)
            
        return results

    def export_graph(self, format: str = 'turtle', file_path: Optional[str] = None) -> Optional[str]:
        """
        Export the graph in the specified format.
        
        Args:
            format (str): Format to export (turtle, xml, n3, etc.)
            file_path (Optional[str]): Path to save the exported graph
            
        Returns:
            Optional[str]: String representation of the graph if no file_path is provided
        """
        if file_path:
            self.graph.serialize(destination=file_path, format=format)
            return None
        return self.graph.serialize(format=format)

    def import_graph(self, file_path: str, format: str = 'turtle') -> None:
        """
        Import a graph from a file.
        
        Args:
            file_path (str): Path to the file to import
            format (str): Format of the input file
        """
        self.graph.parse(file_path, format=format)

    def get_all_triples(self) -> List[Tuple[str, str, str]]:
        """
        Get all triples in the graph.
        
        Returns:
            List[Tuple[str, str, str]]: List of all triples
        """
        return [(str(s), str(p), str(o)) for s, p, o in self.graph] 