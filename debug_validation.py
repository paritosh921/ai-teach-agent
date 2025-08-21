#!/usr/bin/env python3
"""
Debug script to identify the YAML validation issue
"""

import yaml
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from schemas.video_schema import validate_video_yaml, ValidationError

def debug_yaml_validation():
    """Debug the YAML validation issue"""
    
    # Read the problematic YAML file
    yaml_file = "output/builder/understanding_limits_1755775365_spec.yaml"
    
    with open(yaml_file, 'r') as f:
        yaml_content = f.read()
    
    print("=== YAML Content Analysis ===")
    parsed = yaml.safe_load(yaml_content)
    
    print(f"Top level keys: {list(parsed.keys())}")
    print(f"Number of scenes: {len(parsed.get('scenes', []))}")
    
    scenes = parsed.get('scenes', [])
    for i, scene in enumerate(scenes):
        print(f"\nScene {i} (ID: {scene.get('id', 'unknown')}):")
        print(f"  Keys: {list(scene.keys())}")
        
        if 'layout' in scene:
            layout = scene['layout']
            print(f"  Layout keys: {list(layout.keys())}")
            
            if 'elements' in layout:
                elements = layout['elements']
                print(f"  Elements type: {type(elements)}")
                print(f"  Elements length: {len(elements) if isinstance(elements, list) else 'N/A'}")
                
                if isinstance(elements, list) and len(elements) > 0:
                    print(f"  First element keys: {list(elements[0].keys())}")
                else:
                    print(f"  WARNING: Elements is empty or not a list!")
            else:
                print(f"  WARNING: No 'elements' key in layout!")
        else:
            print(f"  WARNING: No 'layout' key in scene!")
    
    print("\n=== Attempting Validation ===")
    try:
        validate_video_yaml(parsed)
        print("SUCCESS: YAML validation passed!")
    except ValidationError as e:
        print(f"ERROR: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    debug_yaml_validation()
