#!/usr/bin/env python3
"""
Check what class_19102 maps to in ImageNet-21k
"""

import json

def check_acorn_class():
    """Check what class_19102 corresponds to"""
    
    # Load the mapping
    with open('imagenet21k_wordnet_mapping.json', 'r') as f:
        mapping = json.load(f)
    
    # Check class_19102
    class_id = "19102"
    if class_id in mapping:
        print(f"✅ Class {class_id} found: {mapping[class_id]}")
    else:
        print(f"❌ Class {class_id} not found in mapping")
    
    # Search for acorn-related classes
    acorn_classes = []
    for class_idx, class_info in mapping.items():
        if 'acorn' in class_info.get('label', '').lower():
            acorn_classes.append((class_idx, class_info))
    
    print(f"\n🔍 Found {len(acorn_classes)} acorn-related classes:")
    for class_idx, class_info in acorn_classes:
        print(f"  {class_idx}: {class_info}")
    
    # Check if mapping has ImageNet-1k equivalents
    print(f"\n📊 Total classes in mapping: {len(mapping)}")
    
    # Look for classes with WordNet synsets
    synset_classes = []
    for class_idx, class_info in mapping.items():
        if 'id' in class_info and 'n12267677' in class_info['id']:  # acorn synset
            synset_classes.append((class_idx, class_info))
    
    print(f"\n🌰 Found {len(synset_classes)} classes with acorn synset (n12267677):")
    for class_idx, class_info in synset_classes:
        print(f"  {class_idx}: {class_info}")

if __name__ == "__main__":
    check_acorn_class() 