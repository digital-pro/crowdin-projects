#!/usr/bin/env python3
"""
Analyze Detection Anomaly
Why are we getting hundreds of detections for terms that should only appear once?
"""

import json

def analyze_detection_anomaly():
    """Analyze why we're getting excessive detections"""
    
    print("🔍 ANALYZING DETECTION ANOMALY")
    print("=" * 80)
    
    # Load results
    with open('fixed_hybrid_results_1751844198.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data.get('analysis_results', [])
    detection_freq = data.get('detection_frequency', {})
    
    print(f"📊 Total images analyzed: {len(results)}")
    print(f"📊 Total detection frequency entries: {len(detection_freq)}")
    
    # Expected mapping: each vocab term should appear in exactly ONE image
    expected_mapping = {}
    for result in results:
        screenshot_id = result.get('screenshot_id')
        expected_vocab = result.get('expected_vocab')
        if screenshot_id and expected_vocab:
            expected_mapping[expected_vocab] = screenshot_id
    
    print(f"\n📋 EXPECTED VOCABULARY MAPPING (1 term = 1 image):")
    print("-" * 60)
    for vocab, screenshot in sorted(expected_mapping.items())[:10]:
        print(f"  {vocab} → vocab-{screenshot}")
    print(f"  ... and {len(expected_mapping) - 10} more")
    
    # Analyze problematic cases
    print(f"\n🚨 DETECTION ANOMALIES:")
    print("-" * 60)
    
    problematic_terms = []
    for vocab_term, count in detection_freq.items():
        expected_screenshot = expected_mapping.get(vocab_term)
        if expected_screenshot:
            # This term should only appear in ONE image (4 grid cells max)
            max_expected = 4  # 4 grid cells per image
            if count > max_expected:
                problematic_terms.append((vocab_term, count, expected_screenshot, count - max_expected))
    
    # Sort by excess detections
    problematic_terms.sort(key=lambda x: x[3], reverse=True)
    
    print(f"Found {len(problematic_terms)} terms with excessive detections:")
    for vocab_term, total_count, expected_screenshot, excess in problematic_terms[:15]:
        print(f"  {vocab_term}: {total_count} detections (expected ≤4, excess: {excess}) → should only be in vocab-{expected_screenshot}")
    
    # Analyze where these excessive detections are coming from
    print(f"\n🔍 ANALYZING WHERE EXCESSIVE DETECTIONS COME FROM:")
    print("-" * 60)
    
    # Take the top problematic case (acorn with 465 detections)
    if problematic_terms:
        top_problem = problematic_terms[0]
        vocab_term, total_count, expected_screenshot, excess = top_problem
        
        print(f"\n📸 ANALYZING '{vocab_term}' (465 detections, should only be in vocab-{expected_screenshot}):")
        print("-" * 60)
        
        # Find all images where this term was detected
        images_with_term = []
        for result in results:
            screenshot_id = result.get('screenshot_id')
            grid_results = result.get('grid_results', {})
            
            term_found_in_image = False
            grid_detections = []
            
            for position, cell_data in grid_results.items():
                vocab_matches = cell_data.get('vocab_matches', [])
                for match in vocab_matches:
                    if match.get('vocab_term') == vocab_term:
                        term_found_in_image = True
                        confidence = match.get('prediction', {}).get('confidence_percent', 0)
                        grid_detections.append((position, confidence))
            
            if term_found_in_image:
                images_with_term.append((screenshot_id, grid_detections))
        
        print(f"'{vocab_term}' was detected in {len(images_with_term)} different images:")
        for screenshot_id, grid_detections in images_with_term[:10]:  # Show first 10
            expected_here = screenshot_id == expected_screenshot
            status = "✅ CORRECT" if expected_here else "❌ FALSE POSITIVE"
            print(f"  vocab-{screenshot_id}: {status} - {len(grid_detections)} grid cells")
            for position, confidence in grid_detections:
                print(f"    {position}: {confidence:.1f}%")
        
        if len(images_with_term) > 10:
            print(f"  ... and {len(images_with_term) - 10} more images with false positive detections")
    
    # Check class mapping quality
    print(f"\n🗺️ CLASS MAPPING ANALYSIS:")
    print("-" * 60)
    
    class_mappings = data.get('class_mapping', {})
    
    # Count how many class indices map to each vocabulary term
    vocab_to_classes = {}
    for class_idx, vocab_term in class_mappings.items():
        if vocab_term not in vocab_to_classes:
            vocab_to_classes[vocab_term] = []
        vocab_to_classes[vocab_term].append(class_idx)
    
    print(f"Vocabulary terms with multiple class mappings (potential cause of over-detection):")
    for vocab_term, class_indices in sorted(vocab_to_classes.items()):
        if len(class_indices) > 1:
            print(f"  {vocab_term}: {len(class_indices)} classes → {class_indices[:5]}{'...' if len(class_indices) > 5 else ''}")
    
    # Analysis summary
    print(f"\n💡 ROOT CAUSE ANALYSIS:")
    print("-" * 60)
    print(f"1. ❌ MULTIPLE CLASS MAPPINGS: Many vocabulary terms are mapped to multiple EfficientNet classes")
    print(f"2. ❌ FALSE POSITIVE SPREAD: These classes are being detected in images where they shouldn't appear")
    print(f"3. ❌ OVER-GENEROUS MAPPING: The hybrid approach may be creating too many class→vocab mappings")
    print(f"4. ❌ CROSS-CONTAMINATION: Classes learned from one image are being detected in other images")
    
    print(f"\n🔧 POTENTIAL SOLUTIONS:")
    print("-" * 60)
    print(f"1. 🎯 STRICTER VALIDATION: Only allow class mappings in the expected image")
    print(f"2. 🧹 CLEANUP PHASE: Remove mappings that appear in wrong images")
    print(f"3. 📍 LOCATION-AWARE MAPPING: Tie class mappings to specific images")
    print(f"4. 🔒 SINGLE-CLASS POLICY: Limit each vocabulary term to one best class mapping")

if __name__ == "__main__":
    analyze_detection_anomaly() 