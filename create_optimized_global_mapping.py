#!/usr/bin/env python3
"""
Create Optimized Global Mapping
Balance between accuracy and usefulness by creating global mappings from high-confidence detections
"""

import json
import time
from collections import Counter, defaultdict

def create_optimized_global_mapping():
    """Create optimized global mapping from location-aware results"""
    
    print("🎯 CREATING OPTIMIZED GLOBAL MAPPING")
    print("=" * 80)
    
    # Load location-aware results
    with open('location_aware_results_1751859471.json', 'r', encoding='utf-8') as f:
        location_data = json.load(f)
    
    analysis_results = location_data.get('analysis_results', [])
    
    # Extract high-confidence detections
    high_confidence_mappings = defaultdict(list)  # class_idx -> [(vocab_term, confidence, image_id)]
    
    print("🔍 Extracting high-confidence detections (>70%)...")
    
    for result in analysis_results:
        image_id = result.get('screenshot_id')
        expected_vocab = result.get('expected_vocab')
        grid_results = result.get('grid_results', {})
        
        for position, cell_data in grid_results.items():
            vocab_matches = cell_data.get('vocab_matches', [])
            
            for match in vocab_matches:
                vocab_term = match.get('vocab_term')
                confidence = match.get('prediction', {}).get('confidence_percent', 0)
                class_idx = match.get('class_idx')
                
                # Only consider high-confidence detections
                if confidence > 70.0 and class_idx and vocab_term:
                    high_confidence_mappings[class_idx].append((vocab_term, confidence, image_id))
    
    print(f"Found {len(high_confidence_mappings)} EfficientNet classes with high-confidence detections")
    
    # Create consistent global mappings
    print("\n🧹 Creating consistent global mappings...")
    
    global_mapping = {}
    mapping_stats = {}
    
    for class_idx, detections in high_confidence_mappings.items():
        # Group by vocabulary term
        vocab_groups = defaultdict(list)
        for vocab_term, confidence, image_id in detections:
            vocab_groups[vocab_term].append((confidence, image_id))
        
        # Find the most consistent vocabulary term for this class
        best_vocab = None
        best_score = 0
        
        for vocab_term, confidences_images in vocab_groups.items():
            # Calculate consistency score
            avg_confidence = sum(conf for conf, _ in confidences_images) / len(confidences_images)
            occurrence_count = len(confidences_images)
            consistency_score = avg_confidence * occurrence_count
            
            if consistency_score > best_score:
                best_score = consistency_score
                best_vocab = vocab_term
        
        # Only add mapping if it's strong enough
        if best_vocab and best_score > 70:  # Minimum threshold
            global_mapping[class_idx] = best_vocab
            mapping_stats[class_idx] = {
                'vocab_term': best_vocab,
                'avg_confidence': sum(conf for conf, _ in vocab_groups[best_vocab]) / len(vocab_groups[best_vocab]),
                'occurrence_count': len(vocab_groups[best_vocab]),
                'consistency_score': best_score,
                'images': [img for _, img in vocab_groups[best_vocab]]
            }
    
    print(f"Created {len(global_mapping)} consistent global mappings")
    
    # Quality control - limit detections per vocabulary term
    print("\n🔒 Applying quality control...")
    
    vocab_term_classes = defaultdict(list)
    for class_idx, vocab_term in global_mapping.items():
        vocab_term_classes[vocab_term].append(class_idx)
    
    # Remove excess mappings for over-represented terms
    max_classes_per_term = 3
    filtered_mapping = {}
    
    for vocab_term, class_indices in vocab_term_classes.items():
        # Sort by consistency score (best first)
        sorted_classes = sorted(class_indices, 
                              key=lambda x: mapping_stats[x]['consistency_score'], 
                              reverse=True)
        
        # Keep only top classes for this vocabulary term
        for class_idx in sorted_classes[:max_classes_per_term]:
            filtered_mapping[class_idx] = vocab_term
    
    print(f"After quality control: {len(filtered_mapping)} mappings")
    
    # Calculate expected detection rates
    print("\n📊 Expected detection rates:")
    print("-" * 60)
    
    vocab_detection_counts = Counter()
    for class_idx, vocab_term in filtered_mapping.items():
        expected_detections = mapping_stats[class_idx]['occurrence_count']
        vocab_detection_counts[vocab_term] += expected_detections
    
    # Show top vocabulary terms
    for vocab_term, expected_count in vocab_detection_counts.most_common(20):
        classes = [k for k, v in filtered_mapping.items() if v == vocab_term]
        avg_conf = sum(mapping_stats[c]['avg_confidence'] for c in classes) / len(classes)
        print(f"  {vocab_term}: {expected_count} detections, {len(classes)} classes, {avg_conf:.1f}% avg confidence")
    
    # Save the optimized mapping
    timestamp = int(time.time())
    output_data = {
        'global_mapping': filtered_mapping,
        'mapping_statistics': mapping_stats,
        'vocabulary_detection_counts': dict(vocab_detection_counts),
        'creation_timestamp': timestamp,
        'total_mappings': len(filtered_mapping),
        'vocabulary_terms_covered': len(vocab_detection_counts),
        'quality_control': {
            'min_confidence': 70.0,
            'min_consistency_score': 70.0,
            'max_classes_per_term': max_classes_per_term
        }
    }
    
    filename = f"optimized_global_mapping_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Optimized global mapping saved to: {filename}")
    
    # Show mapping quality
    print(f"\n✅ OPTIMIZED MAPPING QUALITY:")
    print("-" * 60)
    print(f"📊 Total mappings: {len(filtered_mapping)}")
    print(f"📚 Vocabulary terms covered: {len(vocab_detection_counts)}")
    print(f"🎯 Average detections per term: {sum(vocab_detection_counts.values()) / len(vocab_detection_counts):.1f}")
    print(f"🔒 Max classes per term: {max_classes_per_term}")
    print(f"⚡ High confidence only: >70%")
    
    # Show some example mappings
    print(f"\n🔍 EXAMPLE MAPPINGS:")
    print("-" * 60)
    
    example_terms = ['acorn', 'artichoke', 'bamboo', 'carrot', 'hamster']
    for term in example_terms:
        classes = [k for k, v in filtered_mapping.items() if v == term]
        if classes:
            stats = [mapping_stats[c] for c in classes]
            avg_conf = sum(s['avg_confidence'] for s in stats) / len(stats)
            total_occurrences = sum(s['occurrence_count'] for s in stats)
            print(f"  {term}: {len(classes)} classes, {total_occurrences} expected detections, {avg_conf:.1f}% confidence")
            print(f"    Classes: {classes}")
        else:
            print(f"  {term}: No mapping found")
    
    return filtered_mapping, output_data

if __name__ == "__main__":
    global_mapping, output_data = create_optimized_global_mapping() 