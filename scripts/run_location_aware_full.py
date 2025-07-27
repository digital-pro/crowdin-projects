#!/usr/bin/env python3
"""
Run Full Location-Aware Analysis
Compare with previous over-detection results
"""

import json
import time
from location_aware_analyzer import LocationAwareAnalyzer

def run_full_location_aware_analysis():
    """Run the complete location-aware analysis"""
    
    print("🎯 RUNNING FULL LOCATION-AWARE ANALYSIS")
    print("🔒 This will prevent cross-contamination and over-detection")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = LocationAwareAnalyzer()
    
    # Run complete analysis
    results = analyzer.run_location_aware_analysis()
    
    # Save results
    timestamp = int(time.time())
    results_filename = f"location_aware_results_{timestamp}.json"
    
    output_data = {
        'analysis_results': results,
        'image_specific_mappings': analyzer.image_specific_mappings,
        'detection_frequency': dict(analyzer.detection_frequency),
        'total_cells_analyzed': analyzer.total_cells_analyzed,
        'analysis_type': 'location_aware'
    }
    
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_filename}")
    
    # Compare with previous results
    print(f"\n📊 COMPARISON WITH PREVIOUS RESULTS:")
    print("=" * 80)
    
    try:
        # Load previous results
        with open('fixed_hybrid_results_1751844198.json', 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        old_detection_freq = old_data.get('detection_frequency', {})
        new_detection_freq = analyzer.detection_frequency
        
        print(f"🔍 DETECTION COUNT COMPARISON:")
        print("-" * 60)
        
        # Compare key problematic terms
        problematic_terms = ['acorn', 'antenna', 'artichoke', 'bouquet', 'aloe', 'blender', 'bamboo']
        
        for term in problematic_terms:
            old_count = old_detection_freq.get(term, 0)
            new_count = new_detection_freq.get(term, 0)
            improvement = old_count - new_count
            
            if improvement > 0:
                status = f"✅ FIXED ({improvement} fewer)"
            elif new_count <= 4:
                status = "✅ REASONABLE"
            else:
                status = "❌ STILL HIGH"
            
            print(f"  {term}: {old_count} → {new_count} {status}")
        
        # Calculate overall metrics
        successful_results = [r for r in results if r.get('success')]
        correct_detections = sum(1 for r in successful_results if r.get('has_correct_detection'))
        images_with_detections = sum(1 for r in successful_results if r.get('has_any_detection'))
        
        old_results = old_data.get('analysis_results', [])
        old_successful = [r for r in old_results if r.get('success')]
        old_correct = sum(1 for r in old_successful if r.get('has_correct_detection'))
        old_with_detections = sum(1 for r in old_successful if r.get('has_any_detection'))
        
        print(f"\n📈 OVERALL PERFORMANCE COMPARISON:")
        print("-" * 60)
        print(f"Accuracy: {old_correct/len(old_successful)*100:.1f}% → {correct_detections/len(successful_results)*100:.1f}%")
        print(f"Detection rate: {old_with_detections/len(old_successful)*100:.1f}% → {images_with_detections/len(successful_results)*100:.1f}%")
        print(f"Total detections: {sum(old_detection_freq.values())} → {sum(new_detection_freq.values())}")
        
    except FileNotFoundError:
        print("Previous results file not found for comparison")
    
    # Key test cases
    print(f"\n🧪 KEY TEST CASES:")
    print("-" * 60)
    
    test_cases = ['004', '007', '008', '009', '010', '018', '034', '153']
    for test_id in test_cases:
        result = next((r for r in results if r.get('screenshot_id') == test_id), None)
        if result:
            expected = result.get('expected_vocab')
            correct = result.get('has_correct_detection')
            status = "✅ CORRECT" if correct else "❌ INCORRECT"
            print(f"  vocab-{test_id} ({expected}): {status}")
    
    print(f"\n🎉 LOCATION-AWARE ANALYSIS COMPLETE!")
    print(f"📊 Results file: {results_filename}")
    print(f"🔒 Each vocabulary term is now limited to its correct image only")

if __name__ == "__main__":
    run_full_location_aware_analysis() 