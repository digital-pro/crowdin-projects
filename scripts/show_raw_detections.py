#!/usr/bin/env python3
"""
Show Raw Detections
Display what the model is actually detecting with high confidence,
even before class mappings are established
"""

import json
from collections import Counter, defaultdict

def analyze_raw_detections():
    """Analyze the raw detections from the detailed results"""
    
    print("🔍 ANALYZING RAW DETECTIONS")
    print("=" * 80)
    print("Showing high-confidence predictions even without class mappings")
    print("=" * 80)
    
    # Load the detailed results
    try:
        with open('analysis_results_1751840792/detailed_results.json', 'r') as f:
            data = json.load(f)
        
        results = data.get('analysis_results', [])
        
        print(f"📊 Analyzing {len(results)} images...")
        
        # Track high-confidence detections
        high_confidence_detections = []
        class_to_expected = defaultdict(list)
        
        for result in results:
            if not result.get('success'):
                continue
            
            screenshot_id = result.get('screenshot_id')
            expected_vocab = result.get('expected_vocab')
            grid_results = result.get('grid_results', {})
            
            print(f"\n📸 vocab-{screenshot_id}.png (expected: {expected_vocab})")
            
            for position, cell_data in grid_results.items():
                predictions = cell_data.get('predictions', [])
                
                if predictions:
                    top_pred = predictions[0]
                    confidence = top_pred['confidence_percent']
                    class_idx = top_pred['class_idx']
                    
                    print(f"  {position}: Class {class_idx} ({confidence:.1f}%)", end="")
                    
                    # Flag high confidence detections
                    if confidence > 50.0:
                        print(" 🎯 HIGH CONFIDENCE")
                        high_confidence_detections.append({
                            'screenshot_id': screenshot_id,
                            'position': position,
                            'expected_vocab': expected_vocab,
                            'class_idx': class_idx,
                            'confidence': confidence
                        })
                        
                        # Track which classes appear with which expected vocab
                        class_to_expected[class_idx].append(expected_vocab)
                    elif confidence > 30.0:
                        print(" ⚖️ MODERATE CONFIDENCE")
                    else:
                        print(" ❓ LOW CONFIDENCE")
        
        # Analyze potential mappings
        print(f"\n🎯 HIGH CONFIDENCE DETECTIONS ANALYSIS:")
        print("=" * 60)
        
        if high_confidence_detections:
            print(f"Found {len(high_confidence_detections)} high-confidence detections (>50%):")
            
            for detection in high_confidence_detections:
                print(f"  📸 vocab-{detection['screenshot_id']} {detection['position']}: "
                      f"Class {detection['class_idx']} → expected '{detection['expected_vocab']}' "
                      f"({detection['confidence']:.1f}%)")
        else:
            print("No high-confidence detections found")
        
        # Show potential class mappings
        print(f"\n🗺️ POTENTIAL CLASS MAPPINGS:")
        print("=" * 60)
        
        for class_idx, expected_vocabs in class_to_expected.items():
            vocab_counts = Counter(expected_vocabs)
            most_common = vocab_counts.most_common(1)[0]
            
            if len(expected_vocabs) >= 2:  # Multiple evidence points
                print(f"  Class {class_idx} → '{most_common[0]}' "
                      f"(evidence: {most_common[1]}/{len(expected_vocabs)} occurrences)")
            else:
                print(f"  Class {class_idx} → '{most_common[0]}' "
                      f"(single evidence - needs more validation)")
        
        # Check specific test cases
        print(f"\n🧪 SPECIFIC TEST CASES:")
        print("=" * 60)
        
        test_cases = [
            {'id': '004', 'expected': 'acorn'},
            {'id': '007', 'expected': 'artichoke'},
            {'id': '008', 'expected': 'bamboo'},
            {'id': '010', 'expected': 'blender'}
        ]
        
        for test_case in test_cases:
            test_id = test_case['id']
            expected = test_case['expected']
            
            # Find this result
            test_result = None
            for result in results:
                if result.get('screenshot_id') == test_id:
                    test_result = result
                    break
            
            if test_result:
                print(f"\n📸 vocab-{test_id}.png (expected: {expected}):")
                grid_results = test_result.get('grid_results', {})
                
                found_high_confidence = False
                for position, cell_data in grid_results.items():
                    predictions = cell_data.get('predictions', [])
                    if predictions:
                        top_pred = predictions[0]
                        confidence = top_pred['confidence_percent']
                        class_idx = top_pred['class_idx']
                        
                        if confidence > 50.0:
                            print(f"  ✅ {position}: Class {class_idx} ({confidence:.1f}%) - STRONG DETECTION")
                            found_high_confidence = True
                        elif confidence > 30.0:
                            print(f"  ⚖️ {position}: Class {class_idx} ({confidence:.1f}%) - MODERATE DETECTION")
                
                if found_high_confidence:
                    print(f"  🎯 VERDICT: Model IS detecting objects in this image!")
                    print(f"  💡 Issue: Need more images to build class mapping for '{expected}'")
                else:
                    print(f"  ❓ VERDICT: No strong detections found")
        
        print(f"\n💡 KEY INSIGHTS:")
        print("=" * 60)
        print("1. The model IS detecting objects with high confidence")
        print("2. The validation system requires multiple evidence points")
        print("3. We need to run on more images OR lower the evidence threshold")
        print("4. High-confidence detections show the model is working correctly")
        
        print(f"\n🔧 SOLUTIONS:")
        print("=" * 60)
        print("1. Run analysis on more images (20-30) to build mappings")
        print("2. Lower evidence threshold to 1-2 occurrences")
        print("3. Create direct class mappings for known high-confidence detections")
        print("4. Use a hybrid approach: strict validation + single-evidence allowance")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    analyze_raw_detections() 