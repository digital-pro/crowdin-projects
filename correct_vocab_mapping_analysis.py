#!/usr/bin/env python3
"""
Corrected Vocabulary Mapping Analysis
Maps screenshot IDs to correct vocabulary terms from vocab_list.txt
"""

import json
import os

def load_vocab_list():
    """Load the vocabulary list from vocab_list.txt"""
    try:
        with open('vocab/vocab_list.txt', 'r') as f:
            vocab_list = [line.strip() for line in f.readlines() if line.strip()]
        return vocab_list
    except FileNotFoundError:
        print("❌ vocab_list.txt not found!")
        return []

def get_expected_vocab(screenshot_id, vocab_list):
    """Get expected vocabulary term for a screenshot ID"""
    try:
        # Convert screenshot ID to index (1-based to 0-based)
        index = int(screenshot_id) - 1
        if 0 <= index < len(vocab_list):
            return vocab_list[index]
        return None
    except (ValueError, IndexError):
        return None

def analyze_corrected_results():
    """Analyze results with correct vocabulary mapping"""
    
    # Load vocabulary list
    vocab_list = load_vocab_list()
    if not vocab_list:
        return
    
    print(f"📚 Loaded {len(vocab_list)} vocabulary terms")
    
    # Find the latest complete results file
    results_files = [f for f in os.listdir('.') if f.startswith('complete_170_vocab_analysis_') and f.endswith('.json')]
    if not results_files:
        print("❌ No complete results file found!")
        return
    
    latest_file = max(results_files, key=lambda x: os.path.getmtime(x))
    print(f"📁 Reading results from: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('analysis_results', [])
        
        print(f"\n🔍 CORRECTED VOCABULARY MAPPING ANALYSIS")
        print("=" * 80)
        
        # Test specific cases with correct mapping
        test_cases = [
            ("001", "acorn"),      # vocab-001.png = acorn (line 1)
            ("004", "artichoke"),  # vocab-004.png = artichoke (line 4)
            ("007", "blower"),     # vocab-007.png = blower (line 7)
            ("015", "carrot"),     # vocab-015.png = carrot (line 15)
            ("031", "hamster"),    # vocab-031.png = hamster (line 31)
            ("050", "pump"),       # vocab-050.png = pump (line 50)
            ("100", "turkey"),     # vocab-100.png = turkey (line 100)
            ("150", "bandage"),    # vocab-150.png = bandage (line 150)
        ]
        
        print(f"🧪 TESTING WITH CORRECT VOCABULARY MAPPING:")
        print("-" * 60)
        
        correct_identifications = 0
        total_tested = 0
        
        for screenshot_id, expected_term in test_cases:
            # Verify expected term matches vocab list
            vocab_index = int(screenshot_id) - 1
            actual_expected = vocab_list[vocab_index] if vocab_index < len(vocab_list) else None
            
            if actual_expected != expected_term:
                print(f"⚠️  Mismatch: vocab-{screenshot_id} expected {expected_term}, but vocab list has {actual_expected}")
                continue
            
            # Find this result in our data
            test_result = None
            for result in results:
                if result.get('screenshot_id') == screenshot_id:
                    test_result = result
                    break
            
            if test_result and test_result.get('success'):
                found_expected = False
                matches_found = []
                all_matches = []
                
                for position, cell_data in test_result.get('grid_results', {}).items():
                    if cell_data.get('vocab_matches'):
                        for match in cell_data['vocab_matches']:
                            if match.get('vocab_term'):
                                all_matches.append(f"{match['vocab_term']} ({match.get('similarity', 0):.1f})")
                                if match['vocab_term'].lower() == expected_term.lower():
                                    matches_found.append(f"✅ {match['vocab_term']} in {position}")
                                    found_expected = True
                                elif len(matches_found) < 2:  # Show top 2 non-matching results
                                    matches_found.append(f"❌ {match['vocab_term']} in {position}")
                
                result_text = f"Found: {', '.join(matches_found[:3])}" if matches_found else "No matches"
                status = "✅ CORRECT" if found_expected else "❌ MISSED"
                
                if found_expected:
                    correct_identifications += 1
                total_tested += 1
                
                print(f"   vocab-{screenshot_id} ({expected_term}): {status}")
                print(f"      {result_text}")
                if len(all_matches) > 3:
                    print(f"      All matches: {', '.join(all_matches[:5])}...")
                print()
            else:
                print(f"   vocab-{screenshot_id} ({expected_term}): ❌ NO DATA")
                total_tested += 1
        
        # Calculate accuracy
        accuracy = (correct_identifications / total_tested * 100) if total_tested > 0 else 0
        print(f"📊 CORRECTED ACCURACY RESULTS:")
        print(f"   ✅ Correct identifications: {correct_identifications}/{total_tested}")
        print(f"   🎯 Accuracy rate: {accuracy:.1f}%")
        
        # Show vocabulary list sample
        print(f"\n📋 VOCABULARY LIST SAMPLE (first 20 terms):")
        for i, term in enumerate(vocab_list[:20], 1):
            print(f"   {i:3d}. {term}")
        
        # Analyze all results for correct matches
        print(f"\n🔍 ANALYZING ALL 170 SCREENSHOTS:")
        print("-" * 60)
        
        total_correct = 0
        total_analyzed = 0
        
        for result in results:
            screenshot_id = result.get('screenshot_id')
            if not screenshot_id:
                continue
                
            try:
                expected_term = get_expected_vocab(screenshot_id, vocab_list)
                if not expected_term:
                    continue
                    
                found_expected = False
                if result.get('success') and result.get('grid_results'):
                    for position, cell_data in result['grid_results'].items():
                        if cell_data.get('vocab_matches'):
                            for match in cell_data['vocab_matches']:
                                if match.get('vocab_term') and match['vocab_term'].lower() == expected_term.lower():
                                    found_expected = True
                                    break
                            if found_expected:
                                break
                
                if found_expected:
                    total_correct += 1
                total_analyzed += 1
                
            except Exception as e:
                continue
        
        overall_accuracy = (total_correct / total_analyzed * 100) if total_analyzed > 0 else 0
        print(f"📊 OVERALL CORRECTED RESULTS:")
        print(f"   📸 Screenshots analyzed: {total_analyzed}")
        print(f"   ✅ Correct vocabulary identifications: {total_correct}")
        print(f"   🎯 Overall accuracy: {overall_accuracy:.1f}%")
        
        # Show some successful identifications
        print(f"\n🏆 SUCCESSFUL IDENTIFICATIONS (sample):")
        success_count = 0
        for result in results[:20]:  # Check first 20
            screenshot_id = result.get('screenshot_id')
            if not screenshot_id:
                continue
                
            expected_term = get_expected_vocab(screenshot_id, vocab_list)
            if not expected_term:
                continue
                
            if result.get('success') and result.get('grid_results'):
                for position, cell_data in result['grid_results'].items():
                    if cell_data.get('vocab_matches'):
                        for match in cell_data['vocab_matches']:
                            if match.get('vocab_term') and match['vocab_term'].lower() == expected_term.lower():
                                confidence = match.get('similarity', 0)
                                print(f"   ✅ vocab-{screenshot_id}: Found '{expected_term}' in {position} ({confidence:.1f}% similarity)")
                                success_count += 1
                                break
                        if success_count >= 10:  # Show max 10 examples
                            break
                if success_count >= 10:
                    break
        
        print(f"\n🎉 CORRECTED ANALYSIS COMPLETE!")
        print(f"The vocabulary mapping has been corrected to match vocab_list.txt")
        
    except Exception as e:
        print(f"❌ Error reading results: {str(e)}")

if __name__ == "__main__":
    analyze_corrected_results() 