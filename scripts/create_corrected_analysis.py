#!/usr/bin/env python3
"""
Create Corrected Analysis
Fix the grid display bug by creating accurate analysis results
"""

import json

def create_corrected_analysis():
    """Create corrected analysis with accurate grid display status"""
    
    print("🔧 CREATING CORRECTED ANALYSIS")
    print("=" * 80)
    
    # Load optimized global results
    with open('optimized_global_results_1751989725.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    analysis_results = data.get('analysis_results', [])
    
    corrected_results = []
    total_top_matches = 0
    total_found_anywhere = 0
    total_not_found = 0
    
    # Process each result
    for result in analysis_results:
        screenshot_id = result.get('screenshot_id')
        expected_vocab = result.get('expected_vocab')
        grid_results = result.get('grid_results', {})
        
        # Check status for each cell
        cells_with_top_match = []
        cells_with_expected_found = []
        cells_with_wrong_top = []
        
        for position, cell_data in grid_results.items():
            vocab_matches = cell_data.get('vocab_matches', [])
            
            if vocab_matches:
                top_match = vocab_matches[0]
                top_term = top_match.get('vocab_term', '').lower()
                
                # Check if expected term is top match
                if top_term == expected_vocab.lower():
                    cells_with_top_match.append(position)
                else:
                    # Check if expected term is found anywhere in this cell
                    expected_found = any(
                        match.get('vocab_term', '').lower() == expected_vocab.lower()
                        for match in vocab_matches
                    )
                    
                    if expected_found:
                        cells_with_expected_found.append(position)
                    else:
                        cells_with_wrong_top.append((position, top_term))
        
        # Determine corrected status
        has_top_match = len(cells_with_top_match) > 0
        has_expected_anywhere = len(cells_with_expected_found) > 0
        has_any_expected = has_top_match or has_expected_anywhere
        
        # Update counters
        if has_top_match:
            total_top_matches += 1
        elif has_any_expected:
            total_found_anywhere += 1
        else:
            total_not_found += 1
        
        # Create corrected result
        corrected_result = result.copy()
        corrected_result.update({
            'has_top_match': has_top_match,
            'has_expected_anywhere': has_any_expected,
            'cells_with_top_match': cells_with_top_match,
            'cells_with_expected_found': cells_with_expected_found,
            'cells_with_wrong_top': cells_with_wrong_top,
            'corrected_status': 'TOP_MATCH' if has_top_match else ('FOUND_ELSEWHERE' if has_any_expected else 'NOT_FOUND')
        })
        
        corrected_results.append(corrected_result)
        
        # Print analysis for problematic cases
        if screenshot_id in ['004', '005', '006', '007', '008', '009']:
            print(f"\n📸 vocab-{screenshot_id} (expected: {expected_vocab})")
            print(f"   Original status: {'✅ CORRECT' if result.get('has_correct_detection') else '❌ INCORRECT'}")
            print(f"   Corrected status: {corrected_result['corrected_status']}")
            
            if cells_with_top_match:
                print(f"   ✅ Top matches in: {cells_with_top_match}")
            
            if cells_with_expected_found:
                print(f"   🔶 Expected found (not top) in: {cells_with_expected_found}")
            
            if cells_with_wrong_top:
                print(f"   ❌ Wrong top matches:")
                for pos, term in cells_with_wrong_top:
                    print(f"      {pos}: '{term}' (should be '{expected_vocab}')")
    
    # Print summary
    print(f"\n📊 CORRECTED ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total images analyzed: {len(corrected_results)}")
    print(f"✅ Expected term is TOP MATCH: {total_top_matches} ({total_top_matches/len(corrected_results)*100:.1f}%)")
    print(f"🔶 Expected term FOUND elsewhere: {total_found_anywhere} ({total_found_anywhere/len(corrected_results)*100:.1f}%)")
    print(f"❌ Expected term NOT FOUND: {total_not_found} ({total_not_found/len(corrected_results)*100:.1f}%)")
    
    print(f"\n🚨 BUG IMPACT:")
    misleading_cases = total_found_anywhere
    print(f"   {misleading_cases} cases show 'CORRECT ✅' but have wrong terms in grid cells")
    print(f"   This represents {misleading_cases/len(corrected_results)*100:.1f}% of all cases")
    
    # Save corrected analysis
    corrected_data = data.copy()
    corrected_data['analysis_results'] = corrected_results
    corrected_data['corrected_statistics'] = {
        'total_images': len(corrected_results),
        'top_match_count': total_top_matches,
        'found_elsewhere_count': total_found_anywhere,
        'not_found_count': total_not_found,
        'top_match_accuracy': total_top_matches / len(corrected_results) * 100,
        'misleading_cases': misleading_cases,
        'misleading_percentage': misleading_cases / len(corrected_results) * 100
    }
    
    output_file = f'corrected_analysis_{int(time.time())}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(corrected_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Corrected analysis saved to: {output_file}")
    
    return corrected_data

def create_visualization_fix():
    """Create a JavaScript fix for the web interface"""
    
    print(f"\n🌐 CREATING WEB INTERFACE FIX")
    print("=" * 80)
    
    js_fix = '''
// Grid Display Bug Fix
// Add this to the HTML to show accurate status

function showCorrectedStatus() {
    // Update status display logic
    const statusUpdates = {
        '004': { expected: 'acorn', topMatch: ['top_left'], foundElsewhere: [], wrongTop: ['top_right: bouquet', 'bottom_left: chat', 'bottom_right: preserve'] },
        '005': { expected: 'aloe', topMatch: ['top_right'], foundElsewhere: [], wrongTop: ['top_left: preserve', 'bottom_left: sandbag', 'bottom_right: sprinkler'] },
        '006': { expected: 'antenna', topMatch: ['top_right'], foundElsewhere: [], wrongTop: ['top_left: foam', 'bottom_left: cloak', 'bottom_right: carousel'] },
        '007': { expected: 'artichoke', topMatch: ['top_right'], foundElsewhere: [], wrongTop: ['top_left: cheese', 'bottom_left: swordfish', 'bottom_right: facade'] },
        '008': { expected: 'bamboo', topMatch: ['top_right', 'bottom_right'], foundElsewhere: [], wrongTop: ['top_left: chat', 'bottom_left: sprinkler'] },
        '009': { expected: 'barrel', topMatch: ['bottom_left'], foundElsewhere: [], wrongTop: ['top_left: foam', 'top_right: antenna', 'bottom_right: preserve'] }
    };
    
    // Apply visual indicators
    Object.entries(statusUpdates).forEach(([imageId, status]) => {
        const imageElement = document.querySelector(`[data-image-id="${imageId}"]`);
        if (imageElement) {
            // Update header status
            const header = imageElement.querySelector('.efficientnet-image-header');
            if (header) {
                const hasTopMatch = status.topMatch.length > 0;
                const statusText = hasTopMatch ? 
                    '✅ CORRECT (Top Match)' : 
                    (status.foundElsewhere.length > 0 ? '🔶 FOUND (Not Top)' : '❌ NOT FOUND');
                
                header.innerHTML = header.innerHTML.replace(
                    /✅ CORRECT|❌ INCORRECT/,
                    statusText
                );
                
                // Update header styling
                header.className = hasTopMatch ? 'correct-detection' : 'partial-detection';
            }
            
            // Update grid cells
            status.wrongTop.forEach(wrongInfo => {
                const [position, wrongTerm] = wrongInfo.split(': ');
                const cell = imageElement.querySelector(`[data-position="${position}"]`);
                if (cell) {
                    cell.innerHTML += `<div style="color: #dc3545; font-size: 0.7em;">❌ Wrong: ${wrongTerm}</div>`;
                    cell.classList.add('wrong-top-match');
                }
            });
        }
    });
    
    console.log('🔧 Grid display corrected for vocab-004 through vocab-009');
}

// Auto-apply when results are loaded
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(showCorrectedStatus, 1000);
});
'''
    
    with open('grid_display_fix.js', 'w', encoding='utf-8') as f:
        f.write(js_fix)
    
    print(f"📄 JavaScript fix saved to: grid_display_fix.js")
    print(f"   Add this script to your HTML to fix the display")

if __name__ == "__main__":
    import time
    create_corrected_analysis()
    create_visualization_fix() 