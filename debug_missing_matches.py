#!/usr/bin/env python3
"""
Debug Missing Vocab Matches
Check why vocab-007 and vocab-008 aren't getting vocab_matches
"""

import json

def debug_missing_matches():
    """Debug why certain high-confidence detections aren't getting vocab matches"""
    
    print("🔍 DEBUGGING MISSING VOCAB MATCHES")
    print("=" * 80)
    
    # Load the hybrid results
    with open('full_hybrid_results/detailed_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    class_mappings = data.get('class_mappings', {})
    results = data.get('analysis_results', [])
    
    print(f"📊 Total class mappings: {len(class_mappings)}")
    
    # Check specific problematic cases
    test_cases = ['007', '008', '009']
    
    for test_id in test_cases:
        print(f"\n📸 DEBUGGING vocab-{test_id}:")
        print("-" * 60)
        
        # Find the result
        result = None
        for r in results:
            if r.get('screenshot_id') == test_id:
                result = r
                break
        
        if not result:
            print(f"❌ No result found for vocab-{test_id}")
            continue
        
        expected = result.get('expected_vocab')
        print(f"Expected vocabulary: {expected}")
        
        # Check each grid cell
        grid_results = result.get('grid_results', {})
        for position, cell_data in grid_results.items():
            predictions = cell_data.get('predictions', [])
            vocab_matches = cell_data.get('vocab_matches', [])
            
            print(f"\n  {position}:")
            print(f"    Vocab matches: {len(vocab_matches)}")
            
            if predictions:
                top_pred = predictions[0]
                class_idx = top_pred['class_idx']
                confidence = top_pred['confidence_percent']
                
                print(f"    Top prediction: Class {class_idx} ({confidence:.1f}%)")
                
                # Check if this class is mapped
                if class_idx in class_mappings:
                    mapped_term = class_mappings[class_idx]
                    print(f"    ✅ Class mapping exists: {class_idx} → '{mapped_term}'")
                    
                    # Check if it matches expected
                    if mapped_term.lower() == expected.lower():
                        print(f"    ✅ Mapping matches expected vocabulary!")
                        if not vocab_matches:
                            print(f"    ❌ BUT NO VOCAB MATCHES FOUND - THIS IS THE BUG!")
                    else:
                        print(f"    ⚠️ Mapping doesn't match expected ('{expected}')")
                else:
                    print(f"    ❌ No class mapping for {class_idx}")
                    
                    # Check if there are similar classes mapped
                    similar_classes = [k for k, v in class_mappings.items() 
                                     if v.lower() == expected.lower()]
                    if similar_classes:
                        print(f"    💡 Other classes mapped to '{expected}': {similar_classes}")
    
    # Check what classes are mapped to artichoke and bamboo
    print(f"\n🔍 CHECKING SPECIFIC MAPPINGS:")
    print("-" * 60)
    
    for target_vocab in ['artichoke', 'bamboo', 'barrel']:
        mapped_classes = [k for k, v in class_mappings.items() 
                         if v.lower() == target_vocab.lower()]
        print(f"'{target_vocab}' mapped to classes: {mapped_classes}")
    
    print(f"\n💡 HYPOTHESIS:")
    print("-" * 60)
    print("The class mappings exist, but the vocab matching logic in")
    print("match_vocabulary_terms_hybrid() has a bug that prevents")
    print("these mappings from being converted to vocab_matches.")

if __name__ == "__main__":
    debug_missing_matches() 