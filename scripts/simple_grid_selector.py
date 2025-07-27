#!/usr/bin/env python3
"""
Simple Grid Selector
For each vocab frame, determine which grid cell the model thinks is most likely 
to contain the expected vocabulary term.
"""

import json
import time

def create_simple_grid_selection():
    """Create simple grid selection results for all 170 frames"""
    
    print("🎯 CREATING SIMPLE GRID SELECTION RESULTS")
    print("=" * 80)
    
    # Load optimized global results
    with open('optimized_global_results_1751989725.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis_results = data.get('analysis_results', [])
    
    simple_results = []
    
    for result in analysis_results:
        screenshot_id = result.get('screenshot_id')
        expected_vocab = result.get('expected_vocab')
        grid_results = result.get('grid_results', {})
        
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
        
        # Create simple result
        simple_result = {
            'screenshot_id': screenshot_id,
            'expected_vocab': expected_vocab,
            'model_selection': best_cell,
            'selection_confidence': best_confidence,
            'expected_found_in_cells': expected_found_cells,
            'all_cell_predictions': cell_predictions,
            'image_url': f'https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/task-screenshots/vocab/vocab-{screenshot_id}.png'
        }
        
        simple_results.append(simple_result)
        
        # Print summary for first few
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
    
    # Save results
    output_data = {
        'metadata': {
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_frames': total_frames,
            'frames_with_selection': frames_with_selection,
            'selection_rate_percent': selection_rate,
            'description': 'Simple grid selection results - which cell does the model think contains the expected vocabulary term?'
        },
        'results': simple_results
    }
    
    output_file = f'simple_grid_selection_{int(time.time())}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return output_data

def analyze_selection_patterns():
    """Analyze patterns in the model's selections"""
    
    print(f"\n🔍 ANALYZING SELECTION PATTERNS")
    print("=" * 80)
    
    # Load the simple results
    with open('optimized_global_results_1751989725.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis_results = data.get('analysis_results', [])
    
    # Count selections by position
    position_counts = {
        'top_left': 0,
        'top_right': 0, 
        'bottom_left': 0,
        'bottom_right': 0,
        'none': 0
    }
    
    # Analyze each result
    for result in analysis_results:
        expected_vocab = result.get('expected_vocab')
        grid_results = result.get('grid_results', {})
        
        # Find best cell for expected term
        best_cell = None
        best_confidence = 0
        
        for position, cell_data in grid_results.items():
            vocab_matches = cell_data.get('vocab_matches', [])
            
            for match in vocab_matches:
                vocab_term = match.get('vocab_term', '').lower()
                confidence = match.get('prediction', {}).get('confidence_percent', 0)
                
                if vocab_term == expected_vocab.lower() and confidence > best_confidence:
                    best_confidence = confidence
                    best_cell = position
        
        if best_cell:
            position_counts[best_cell] += 1
        else:
            position_counts['none'] += 1
    
    print(f"Model selections by grid position:")
    for position, count in position_counts.items():
        percentage = (count / len(analysis_results)) * 100
        print(f"  {position.replace('_', '-')}: {count} selections ({percentage:.1f}%)")

if __name__ == "__main__":
    create_simple_grid_selection()
    analyze_selection_patterns() 