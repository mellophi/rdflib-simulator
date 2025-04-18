"""
Example script demonstrating the use of OntologyDataSimulator with a custom ontology.
"""

from datetime import datetime
from src.utils.ontology_data_simulator import OntologyDataSimulator
import os
import json

def main():
    # Get the absolute path to the ontology file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(current_dir, '..', 'ontology', 'personal_data.owl')
    
    if not os.path.exists(ontology_path):
        print(f"Error: Ontology file not found at {ontology_path}")
        return
    
    # Initialize simulator
    start_date = datetime.now()
    simulator = OntologyDataSimulator(ontology_path, start_date)
    
    # Extract and print ontology structure
    print("\nClasses in ontology:")
    for class_name in simulator.classes:
        print(f"- {class_name}")
        class_info = simulator.classes[class_name]
        print(f"  Label: {class_info['label']}")
        
        # Get properties for this class
        data_props = [prop for prop, info in simulator.data_properties.items() 
                     if class_name in info['domains']]
        object_props = [prop for prop, info in simulator.object_properties.items() 
                       if class_name in info['domains']]
        
        if data_props:
            print("  Data Properties:")
            for prop in data_props:
                print(f"    - {prop}")
                prop_info = simulator.data_properties[prop]
                print(f"      Range: {prop_info['ranges']}")
        
        if object_props:
            print("  Object Properties:")
            for prop in object_props:
                print(f"    - {prop}")
                prop_info = simulator.object_properties[prop]
                print(f"      Range: {prop_info['ranges']}")
        print()
    
    # Generate some example data
    print("\nGenerating example data:")
    generated_data = {}
    
    for class_name in simulator.classes:
        print(f"\nData for {class_name}:")
        try:
            data = simulator.generate_instance_data(class_name)
            print(json.dumps(data, indent=2))
            generated_data[class_name] = data
        except Exception as e:
            print(f"Error generating data: {str(e)}")
    
    # Save generated data
    output_file = os.path.join(current_dir, '..', 'data', 'generated_data.json')
    with open(output_file, 'w') as f:
        json.dump(generated_data, f, indent=2)
    
    print(f"\nGenerated data saved to: {output_file}")
    print("\nSimulation complete!")

if __name__ == "__main__":
    main() 