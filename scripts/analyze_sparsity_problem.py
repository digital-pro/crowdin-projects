#!/usr/bin/env python3
"""
Analyze Sparsity Problem in Location-Aware Results
The location-aware approach fixed over-detection but created sparse, less useful mappings
"""

import json

def analyze_sparsity_problem():
    """Analyze why the location-aware approach creates sparse mappings"""
    
    print("🔍 ANALYZING SPARSITY PROBLEM")
    print("=" * 80)
    
    # Load location-aware results
    with open('location_aware_results_1751859471.json', 'r', encoding='utf-8') as f:
        location_data = json.load(f)
    
    # Load previous over-detection results for comparison
    with open('fixed_hybrid_results_1751844198.json', 'r', encoding='utf-8') as f:
        hybrid_data = json.load(f)
    
    location_mappings = location_data.get('image_specific_mappings', {})
    hybrid_mappings = hybrid_data.get('class_mapping', {})
    
    print(f"📊 MAPPING COMPARISON:")
    print("-" * 60)
    print(f"Location-Aware: {sum(len(mappings) for mappings in location_mappings.values())} total mappings")
    print(f"                {len(location_mappings)} images with mappings")
    print(f"                {sum(len(mappings) for mappings in location_mappings.values()) / len(location_mappings):.1f} mappings per image")
    
    print(f"Hybrid (over-detection): {len(hybrid_mappings)} total mappings")
    print(f"                        Global mappings (used everywhere)")
    
    print(f"\n🚨 THE SPARSITY PROBLEM:")
    print("-" * 60)
    print(f"1. ❌ LOCATION-SPECIFIC ONLY: Each class mapping only works in one image")
    print(f"2. ❌ NO GENERALIZATION: Can't detect 'acorn' in new images")
    print(f"3. ❌ OVERLY RESTRICTIVE: Perfect for training data, useless for real-world")
    print(f"4. ❌ SPARSE COVERAGE: Each vocabulary term locked to one image")
    
    # Show examples of the problem
    print(f"\n📸 EXAMPLES OF SPARSITY:")
    print("-" * 60)
    
    # Check if same EfficientNet classes map to different vocab terms
    class_to_vocab_mapping = {}
    for image_id, mappings in location_mappings.items():
        for class_idx, vocab_term in mappings.items():
            if class_idx not in class_to_vocab_mapping:
                class_to_vocab_mapping[class_idx] = []
            class_to_vocab_mapping[class_idx].append((image_id, vocab_term))
    
    # Find classes that map to different vocabulary terms
    conflicting_classes = {k: v for k, v in class_to_vocab_mapping.items() if len(set(term for _, term in v)) > 1}
    
    print(f"Classes that map to DIFFERENT vocabulary terms in different images:")
    for class_idx, mappings in list(conflicting_classes.items())[:10]:
        vocab_terms = list(set(term for _, term in mappings))
        images = [img for img, _ in mappings]
        print(f"  Class {class_idx}: {vocab_terms} (images: {images})")
    
    print(f"\n💡 WHAT WE NEED:")
    print("-" * 60)
    print(f"1. ✅ GLOBAL MAPPINGS: Classes that work across all images")
    print(f"2. ✅ CONFIDENCE FILTERING: High-confidence mappings only")
    print(f"3. ✅ CONSISTENCY CHECK: Classes that consistently map to same vocab term")
    print(f"4. ✅ GENERALIZATION: Model that works on new, unseen images")
    
    print(f"\n🔧 PROPOSED SOLUTION:")
    print("-" * 60)
    print(f"1. 🎯 CONFIDENCE-BASED GLOBAL MAPPING:")
    print(f"   - Use high-confidence detections (>70%) from location-aware analysis")
    print(f"   - Create global mappings that work across all images")
    print(f"   - Filter out inconsistent mappings")
    
    print(f"2. 🧹 CONSISTENCY VALIDATION:")
    print(f"   - Only keep class→vocab mappings that appear consistently")
    print(f"   - Remove classes that map to multiple different vocab terms")
    print(f"   - Prioritize high-confidence, consistent mappings")
    
    print(f"3. 🔒 QUALITY CONTROL:")
    print(f"   - Limit detections per vocabulary term (max 10-15)")
    print(f"   - Remove mappings that cause over-detection")
    print(f"   - Balance between coverage and precision")
    
    # Analyze what would make good global mappings
    print(f"\n📈 POTENTIAL GLOBAL MAPPINGS:")
    print("-" * 60)
    
    # Find high-confidence, consistent mappings
    consistent_mappings = {}
    for class_idx, mappings in class_to_vocab_mapping.items():
        vocab_terms = [term for _, term in mappings]
        if len(set(vocab_terms)) == 1:  # All map to same vocab term
            vocab_term = vocab_terms[0]
            if vocab_term not in consistent_mappings:
                consistent_mappings[vocab_term] = []
            consistent_mappings[vocab_term].append((class_idx, len(mappings)))
    
    # Show top consistent mappings
    print(f"Vocabulary terms with consistent class mappings:")
    for vocab_term, class_mappings in sorted(consistent_mappings.items())[:15]:
        total_occurrences = sum(count for _, count in class_mappings)
        classes = [class_idx for class_idx, _ in class_mappings]
        print(f"  {vocab_term}: {len(classes)} classes, {total_occurrences} total occurrences")
        if len(classes) <= 3:  # Show details for terms with few classes
            print(f"    Classes: {classes}")
    
    return consistent_mappings

def create_balanced_global_mapping(consistent_mappings):
    """Create a balanced global mapping from consistent mappings"""
    
    print(f"\n🎯 CREATING BALANCED GLOBAL MAPPING:")
    print("-" * 60)
    
    # Create global mapping with quality control
    global_mapping = {}
    vocab_term_counts = {}
    
    for vocab_term, class_mappings in consistent_mappings.items():
        # Sort by occurrence count (more occurrences = more reliable)
        sorted_classes = sorted(class_mappings, key=lambda x: x[1], reverse=True)
        
        # Take top 1-2 classes per vocabulary term to avoid over-detection
        max_classes_per_term = 2
        for class_idx, count in sorted_classes[:max_classes_per_term]:
            if count >= 2:  # Only classes that appear multiple times
                global_mapping[class_idx] = vocab_term
                vocab_term_counts[vocab_term] = vocab_term_counts.get(vocab_term, 0) + count
    
    print(f"Created global mapping with {len(global_mapping)} class mappings")
    print(f"Covering {len(vocab_term_counts)} vocabulary terms")
    
    # Show statistics
    print(f"\nTop vocabulary terms in global mapping:")
    for vocab_term, count in sorted(vocab_term_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        classes = [k for k, v in global_mapping.items() if v == vocab_term]
        print(f"  {vocab_term}: {count} expected detections, {len(classes)} classes")
    
    return global_mapping

if __name__ == "__main__":
    consistent_mappings = analyze_sparsity_problem()
    global_mapping = create_balanced_global_mapping(consistent_mappings) 