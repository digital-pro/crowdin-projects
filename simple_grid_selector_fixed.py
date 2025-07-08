#!/usr/bin/env python3
"""
Fixed Simple Grid Selector
For each vocab frame, determine which grid cell the model thinks is most likely 
to contain the expected vocabulary term - with correct vocabulary mapping.
"""

import json
import time

def load_vocab_list():
    """Load the vocabulary list from file"""
    try:
        with open('vocab/vocab_list.txt', 'r', encoding='utf-8') as f:
            vocab_list = [line.strip() for line in f.readlines() if line.strip()]
        return vocab_list
    except FileNotFoundError:
        print("Warning: vocab_list.txt not found, using default list")
        return ['acorn', 'aloe', 'antenna', 'artichoke', 'bamboo', 'barrel', 'blender', 'blower', 'bouquet', 'buffet']

def create_fixed_grid_selection():
    """Create fixed grid selection results for all 170 frames"""
    
    print("🎯 CREATING FIXED GRID SELECTION RESULTS")
    print("=" * 80)
    
    # Load vocabulary list
    vocab_list = load_vocab_list()
    print(f"Loaded {len(vocab_list)} vocabulary terms")
    
    # Load optimized global results
    with open('optimized_global_results_1751989725.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis_results = data.get('analysis_results', [])
    
    simple_results = []
    
    for result in analysis_results:
        screenshot_id = result.get('screenshot_id')
        grid_results = result.get('grid_results', {})
        
        # Calculate correct expected vocabulary term
        # Screenshots start at 004, vocab list starts at index 0
        screenshot_num = int(screenshot_id)
        vocab_index = screenshot_num - 4  # vocab-004 → index 0, vocab-005 → index 1, etc.
        
        if 0 <= vocab_index < len(vocab_list):
            expected_vocab = vocab_list[vocab_index]
        else:
            expected_vocab = f"unknown_{vocab_index}"
        
        # Find which cell has the highest confidence for the expected vocabulary term
        best_cell = None
        best_confidence = 0
        expected_found_cells = []
        
        # Check each grid cell for the expected term
        for position, cell_data in grid_results.items():
            vocab_matches = cell_data.get('vocab_matches', [])
            
            for match in vocab_matches:
                vocab_term = match.get('vocab_term', '').lower()
                confidence = match.get('prediction', {}).get('confidence_percent', 0)
                
                if vocab_term == expected_vocab.lower():
                    expected_found_cells.append({
                        'position': position,
                        'confidence': confidence
                    })
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_cell = position
        
        # Also get the top prediction for each cell (regardless of whether it's the expected term)
        cell_predictions = {}
        for position, cell_data in grid_results.items():
            vocab_matches = cell_data.get('vocab_matches', [])
            if vocab_matches:
                top_match = vocab_matches[0]
                cell_predictions[position] = {
                    'term': top_match.get('vocab_term'),
                    'confidence': top_match.get('prediction', {}).get('confidence_percent', 0)
                }
            else:
                cell_predictions[position] = {
                    'term': 'No match',
                    'confidence': 0
                }
        
        # Create simple result with better image URLs
        simple_result = {
            'screenshot_id': screenshot_id,
            'expected_vocab': expected_vocab,
            'vocab_index': vocab_index,
            'model_selection': best_cell,
            'selection_confidence': best_confidence,
            'expected_found_in_cells': expected_found_cells,
            'all_cell_predictions': cell_predictions,
            # Try multiple image URL patterns
            'image_urls': [
                f'https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/task-screenshots/vocab/vocab-{screenshot_id}.png',
                f'https://raw.githubusercontent.com/levante-framework/core-tasks/main/task-screenshots/vocab/vocab-{screenshot_id}.png',
                f'https://raw.githubusercontent.com/levante-framework/core-tasks/add-screenshots/task-screenshots/vocab/vocab-{screenshot_id}.png',
                f'/sample_vocab_images/vocab-{screenshot_id}.png'  # Local fallback
            ]
        }
        
        simple_results.append(simple_result)
        
        # Print summary for first 20 and show the vocabulary issue
        if int(screenshot_id) <= 20:
            selection_text = best_cell.replace('_', '-') if best_cell else 'None'
            print(f"vocab-{screenshot_id} (expected: {expected_vocab}) → Model selects: {selection_text}")
            if best_cell:
                print(f"   Confidence: {best_confidence:.1f}%")
            else:
                print(f"   Expected term not found in any cell")
    
    # Calculate summary statistics
    total_frames = len(simple_results)
    frames_with_selection = len([r for r in simple_results if r['model_selection']])
    selection_rate = (frames_with_selection / total_frames) * 100 if total_frames > 0 else 0
    
    print(f"\n📊 SUMMARY")
    print("=" * 80)
    print(f"Total frames analyzed: {total_frames}")
    print(f"Frames where model found expected term: {frames_with_selection} ({selection_rate:.1f}%)")
    print(f"Frames where model couldn't find expected term: {total_frames - frames_with_selection}")
    
    # Show vocabulary mapping examples
    print(f"\n📝 VOCABULARY MAPPING EXAMPLES:")
    print("=" * 80)
    for i in range(min(10, len(simple_results))):
        result = simple_results[i]
        print(f"vocab-{result['screenshot_id']} → \"{result['expected_vocab']}\" (index {result['vocab_index']})")
    
    # Save results
    output_data = {
        'metadata': {
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_frames': total_frames,
            'frames_with_selection': frames_with_selection,
            'selection_rate_percent': selection_rate,
            'vocabulary_list_length': len(vocab_list),
            'description': 'Fixed simple grid selection results - corrected vocabulary mapping and image URLs'
        },
        'vocabulary_list': vocab_list,
        'results': simple_results
    }
    
    output_file = f'simple_grid_selection_fixed_{int(time.time())}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Fixed results saved to: {output_file}")
    
    return output_data

def check_vocabulary_continuity():
    """Check for the vocabulary continuity issue"""
    
    print(f"\n🔍 CHECKING VOCABULARY CONTINUITY")
    print("=" * 80)
    
    vocab_list = load_vocab_list()
    
    # Load results to see what was happening before
    with open('optimized_global_results_1751989725.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis_results = data.get('analysis_results', [])
    
    print(f"Checking first 20 frames:")
    for i, result in enumerate(analysis_results[:20]):
        screenshot_id = result.get('screenshot_id')
        old_expected = result.get('expected_vocab')
        
        # Calculate correct expected vocabulary
        screenshot_num = int(screenshot_id)
        vocab_index = screenshot_num - 4
        
        if 0 <= vocab_index < len(vocab_list):
            correct_expected = vocab_list[vocab_index]
        else:
            correct_expected = f"unknown_{vocab_index}"
        
        status = "✅" if old_expected == correct_expected else "❌"
        print(f"  vocab-{screenshot_id}: {status} Old: '{old_expected}' → Correct: '{correct_expected}'")

if __name__ == "__main__":
    check_vocabulary_continuity()
    create_fixed_grid_selection() 