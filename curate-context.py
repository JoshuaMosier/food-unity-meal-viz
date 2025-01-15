import json
from collections import defaultdict
from typing import Any, Dict, List, Set
import random

def analyze_json_structure(data: Any, path: str = "", max_samples: int = 3) -> Dict:
    """
    Recursively analyze JSON structure and collect information about types, patterns, and samples.
    
    Args:
        data: The JSON data to analyze
        path: Current path in the JSON structure
        max_samples: Maximum number of sample values to collect for each field
        
    Returns:
        Dict containing analysis of the structure
    """
    analysis = {
        "type": type(data).__name__,
        "path": path,
        "samples": set(),
    }
    
    if isinstance(data, dict):
        analysis["keys"] = sorted(list(data.keys()))
        analysis["children"] = {}
        
        for key, value in data.items():
            new_path = f"{path}.{key}" if path else key
            analysis["children"][key] = analyze_json_structure(value, new_path, max_samples)
            
    elif isinstance(data, list):
        analysis["length"] = len(data)
        if data:
            # Analyze structure of list items
            samples = random.sample(data, min(max_samples, len(data)))
            analysis["samples"] = samples
            # Analyze the first item to understand structure of list elements
            analysis["element_structure"] = analyze_json_structure(data[0], f"{path}[]", max_samples)
    else:
        # For primitive types, collect sample values
        analysis["samples"].add(str(data))
        
    return analysis

def print_analysis(analysis: Dict, indent: int = 0) -> None:
    """
    Print the JSON structure analysis in a readable format.
    
    Args:
        analysis: The analysis dictionary
        indent: Current indentation level
    """
    indent_str = "  " * indent
    
    print(f"{indent_str}Type: {analysis['type']}")
    print(f"{indent_str}Path: {analysis['path']}")
    
    if "keys" in analysis:
        print(f"{indent_str}Keys: {', '.join(analysis['keys'])}")
        print(f"{indent_str}Nested structures:")
        for key, child in analysis["children"].items():
            print(f"{indent_str}  {key}:")
            print_analysis(child, indent + 2)
            
    if "length" in analysis:
        print(f"{indent_str}Length: {analysis['length']}")
        print(f"{indent_str}Sample values: {analysis['samples']}")
        if "element_structure" in analysis:
            print(f"{indent_str}Element structure:")
            print_analysis(analysis["element_structure"], indent + 2)
            
    if "samples" in analysis and not isinstance(analysis.get("samples"), list):
        print(f"{indent_str}Sample values: {list(analysis['samples'])[:3]}")

def analyze_json_file(filepath: str) -> None:
    """
    Analyze a JSON file and print its structure.
    
    Args:
        filepath: Path to the JSON file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis = analyze_json_structure(data)
    print("\nJSON Structure Analysis:")
    print("=====================")
    print_analysis(analysis)

# Usage
if __name__ == "__main__":
    analyze_json_file("recipes.json")