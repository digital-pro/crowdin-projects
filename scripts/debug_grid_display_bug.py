#!/usr/bin/env python3
"""
Debug Grid Display Bug
Investigate why vocab-004-009 show wrong terms in grid but claim to be correct
"""

import json

def debug_grid_display_bug():
    """Debug the grid display issue"""
    
    print("🔍 DEBUGGING GRID DISPLAY BUG")
    print("=" * 80)
    
    # Load optimized global results
    with open('optimized_global_results_1751989725.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis_results = data.get('analysis_results', [])
    
    # Check specific problematic cases
    problem_cases = ['004', '005', '006', '007', '008', '009']
    
    for case_id in problem_cases:
        result = next((r for r in analysis_results if r.get('screenshot_id') == case_id), None)
        if not result:
            continue
        
        expected_vocab = result.get('expected_vocab')
        has_correct_detection = result.get('has_correct_detection')
        grid_results = result.get('grid_results', {})
        
        print(f"\n📸 ANALYZING vocab-{case_id} (expected: {expected_vocab})")
        print(f"   Overall result: {'✅ CORRECT' if has_correct_detection else '❌ INCORRECT'}")
        print("-" * 60)
        
        # Check each grid cell
        correct_found_in_cells = []
        wrong_terms_shown = []
        
        for position, cell_data in grid_results.items():
            vocab_matches = cell_data.get('vocab_matches', [])
            
            print(f"   {position}:")
            
            if vocab_matches:
                # Show all matches for this cell
                for i, match in enumerate(vocab_matches):
                    vocab_term = match.get('vocab_term')
                    confidence = match.get('prediction', {}).get('confidence_percent', 0)
                    is_expected = vocab_term.lower() == expected_vocab.lower()
                    
                    status = "✅ EXPECTED" if is_expected else "❌ WRONG"
                    marker = "→" if i == 0 else " "
                    
                    print(f"     {marker} {vocab_term} ({confidence:.1f}%) {status}")
                    
                    if i == 0:  # Top match (what's displayed)
                        if is_expected:
                            correct_found_in_cells.append(position)
                        else:
                            wrong_terms_shown.append((position, vocab_term, confidence))
                    
                    if is_expected and vocab_term not in [p[0] for p in correct_found_in_cells]:
                        correct_found_in_cells.append((position, confidence))
            else:
                print(f"     No vocabulary matches")
        
        # Analysis summary
        print(f"\n   📊 ANALYSIS SUMMARY:")
        if correct_found_in_cells:
            print(f"   ✅ Expected term '{expected_vocab}' found in: {correct_found_in_cells}")
        
        if wrong_terms_shown:
            print(f"   ❌ Wrong terms displayed as top matches:")
            for position, term, conf in wrong_terms_shown:
                print(f"      {position}: '{term}' ({conf:.1f}%) - should be '{expected_vocab}'")
        
        # Check if the "correct" flag is accurate
        actual_correct = len([pos for pos, _, _ in wrong_terms_shown if pos not in [p[0] if isinstance(p, tuple) else p for p in correct_found_in_cells]]) == 0
        
        if has_correct_detection != (len(correct_found_in_cells) > 0):
            print(f"   🚨 BUG DETECTED: has_correct_detection={has_correct_detection} but expected term found in {len(correct_found_in_cells)} cells")
        
        if wrong_terms_shown and has_correct_detection:
            print(f"   🚨 DISPLAY BUG: Shows wrong terms as top matches but claims 'CORRECT'")
            print(f"      This happens when expected term is found but not as the top match in any cell")

def check_mapping_logic():
    """Check if the mapping logic is causing the issue"""
    
    print(f"\n🔍 CHECKING MAPPING LOGIC")
    print("=" * 80)
    
    # Load the global mapping
    with open('optimized_global_mapping_1751927020.json', 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)
    
    global_mapping = mapping_data.get('global_mapping', {})
    
    # Check for conflicting mappings
    vocab_to_classes = {}
    for class_idx, vocab_term in global_mapping.items():
        if vocab_term not in vocab_to_classes:
            vocab_to_classes[vocab_term] = []
        vocab_to_classes[vocab_term].append(class_idx)
    
    print(f"Vocabulary terms with multiple class mappings:")
    problem_terms = []
    for vocab_term, class_indices in vocab_to_classes.items():
        if len(class_indices) > 1:
            problem_terms.append((vocab_term, class_indices))
            print(f"  {vocab_term}: {len(class_indices)} classes → {class_indices}")
    
    if problem_terms:
        print(f"\n🚨 POTENTIAL ISSUE: {len(problem_terms)} vocabulary terms map to multiple classes")
        print(f"   This could cause the same EfficientNet prediction to match multiple vocab terms")
    
    # Check specific problematic terms
    test_terms = ['acorn', 'aloe', 'antenna', 'artichoke', 'bamboo', 'barrel']
    print(f"\n🔍 Checking specific test terms:")
    for term in test_terms:
        if term in vocab_to_classes:
            classes = vocab_to_classes[term]
            print(f"  {term}: {classes}")
        else:
            print(f"  {term}: ❌ NOT MAPPED")

def propose_fix():
    """Propose a fix for the grid display bug"""
    
    print(f"\n🔧 PROPOSED FIX")
    print("=" * 80)
    
    print(f"1. 🎯 ROOT CAUSE:")
    print(f"   - The 'has_correct_detection' flag is set if the expected term appears ANYWHERE in the image")
    print(f"   - But the grid display shows the TOP match for each cell")
    print(f"   - So we can have 'CORRECT' overall but wrong terms displayed in grid cells")
    
    print(f"\n2. 🔧 SOLUTION OPTIONS:")
    print(f"   A. 📊 DISPLAY FIX: Show expected term if found, even if not top match")
    print(f"   B. 🎯 LOGIC FIX: Only mark 'CORRECT' if expected term is top match in at least one cell")
    print(f"   C. 🌈 VISUAL FIX: Color-code cells to show when expected term is found but not top")
    
    print(f"\n3. ✅ RECOMMENDED APPROACH:")
    print(f"   - Use option C: Visual indicators")
    print(f"   - Green: Expected term is top match")
    print(f"   - Blue: Expected term found but not top match")
    print(f"   - Gray: Expected term not found")
    print(f"   - This gives users full transparency about what's happening")

if __name__ == "__main__":
    debug_grid_display_bug()
    check_mapping_logic()
    propose_fix() 